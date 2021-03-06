from django.shortcuts import render, redirect
from django.conf import settings
from django.http import HttpResponse, Http404, HttpResponseBadRequest, HttpResponseForbidden
from django.views.generic import View
from django.views.decorators.clickjacking import xframe_options_exempt
from django.contrib.admin.views.decorators import staff_member_required
from django.core.exceptions import ObjectDoesNotExist
from mturk.queries import get_active_video_turk_task
from .models import *
from mturk.models import Task, FullVideoTask, SingleFrameTask
from .services import *
from datetime import datetime, timezone

import os
import json
import urllib.request
import urllib.parse
import markdown
import sys
import mturk.utils
from mturk.queries import get_active_video_turk_task
from .models import *
from .services import *

import logging
import ast
import cv2

logger = logging.getLogger()

class DataRecord():
    def __init__(self):
        self.hero_name = ''
        self.time = 0
        self.x = 0
        self.y = 0
        self.w = 0
        self.h = 0

def home(request):
    need_annotating = Video.objects.filter(id__gt=0, verified=False)
    return render(request, 'video_list.html', context={
        'videos': need_annotating,
        'thumbnail': True,
        'test': settings.AWS_ID,
        'title': 'Videos'
    })

def statistics(request):
    record_list = []
    hero_skin_dict = {}
    warning_msg = []
    total_num = 0

    all_records = None
    is_image = request.GET.get('image_list')
    print('is_image get value: ',is_image)
    if is_image is None:
        all_records = Video.objects.all()
    else:
        all_records = Video.objects.exclude(image_list='')
    all_labels = Label.objects.all()
    for label in all_labels:
        if label.name in hero_skin_dict:
            msg = "%s is duplicated!" %(label.name)
            warning_msg.append(msg)

        hero_skin_dict[label.name] = 0

    for i in all_records:
        if i.annotation is None:
            msg = "%d [%s] annotation is none" %(i.id, i.filename)
            warning_msg.append(msg)
            continue

        if len(i.annotation) < 20:
            msg = "%d [%s] annotation is invalid" %(i.id, i.filename)
            warning_msg.append(msg)
            continue

        try:
            json_res = json.loads(i.annotation)
            for annotation in json_res:
                hero_name = annotation['type']
                #.encode('utf-8').strip()
                keyframes = annotation["keyframes"]
                hero_num = len(keyframes)

                if hero_name not in hero_skin_dict:
                    msg = "%d [%s] annotation contains invalid label: %s" %(i.id, i.filename, hero_name)
                    warning_msg.append(msg)
                    continue
                    
                hero_skin_dict[hero_name] += hero_num
                total_num += hero_num
            
        except Exception as e:
            warning_msg.append(str(e))
            
    hero_skin_ordered_dict = sorted(hero_skin_dict.items(), key=lambda x: x[1])
    return render(request, 'statistics.html', context={
        'labels_data': hero_skin_ordered_dict,
        'total_num': total_num,
        'warning_msg': warning_msg
    })

def verify_list(request):
    need_verification = Video.objects.filter(id__gt=0, verified=False).exclude(annotation='')[:250]
    return render(request, 'video_list.html', context={
        'videos': need_verification,
        'title': 'Videos to Verify'
    })

def verified_list(request):
    verified = Video.objects.filter(id__gt=0, verified=True).exclude(annotation='')[:100]
    return render(request, 'video_list.html', context={
        'videos': verified,
        'title': 'Verified Videos'
    })

def ready_to_pay(request):
    #tasks = FullVideoTask.objects.filter(paid = False, video__verified = True).exclude(hit_id = '')
    tasks = FullVideoTask.objects.all()#filter(paid = False, video__verified = True).exclude(hit_id = '')
    print("there are {} tasks".format(len(tasks)))
    return render(request, 'turk_ready_to_pay.html', context={
        'tasks': tasks,
    })

def next_unannotated(request, video_id):
    id = Video.objects.filter(id__gt=video_id, annotation='')[0].id
    return redirect('video', id)

# status of Not Published, Published, Awaiting Approval, Verified
# this is a bit convoluted as there's status stored on
# video (approved) as well as FullVideoTask (closed, paid, etc.)
def get_mturk_status(video, full_video_task):
    if video.verified:
        return "Verified"
    if full_video_task == None:
        if video.rejected == True:
            return "Rejected"
        elif video.annotation == '':
            return "Not Published"
        else:
            return "Awaiting Approval"
    if full_video_task.worker_id == '':
        return "Published"
    if full_video_task.worker_id != '':
        return "Awaiting Approval"

@xframe_options_exempt
def video(request, video_id):
    try:
        video = Video.objects.get(id=video_id)
        labels = Label.objects.all()
    except Video.DoesNotExist:
        raise Http404('No video with id "{}". Possible fixes: \n1) Download an up to date DB, see README. \n2) Add this video to the DB via /admin'.format(video_id))

    mturk_data = mturk.utils.authenticate_hit(request)
    if 'error' in mturk_data:
        return HttpResponseForbidden(mturk_data['error'])
    if not (mturk_data['authenticated'] or request.user.is_authenticated()):
        return redirect('/login/?next=' + request.path)

    start_time = float(request.GET['s']) if 's' in request.GET else None
    end_time = float(request.GET['e']) if 'e' in request.GET else None

    turk_task = get_active_video_turk_task(video.id)

    if turk_task != None:
        if turk_task.metrics != '':
            metricsDictr = ast.literal_eval(turk_task.metrics)
        else:
            metricsDictr = {}

        # Data for Javascript
        full_video_task_data = {
            'id': turk_task.id,
            'storedMetrics': metricsDictr,
            'bonus': float(turk_task.bonus),
            'bonusMessage': turk_task.message,
            'rejectionMessage': settings.MTURK_REJECTION_MESSAGE,
            'emailSubject': settings.MTURK_EMAIL_SUBJECT,
            'emailMessage': settings.MTURK_EMAIL_MESSAGE,
            'isComplete': turk_task.worker_id != ''
        }

        # Data for python templating
        if turk_task.last_email_sent_date != None:
            mturk_data['last_email_sent_date'] = turk_task.last_email_sent_date.strftime("%Y-%m-%d %H:%M")
    else:
        full_video_task_data = None

    mturk_data['status'] = get_mturk_status(video, turk_task)
    mturk_data['has_current_full_video_task'] = full_video_task_data != None

    video_data = json.dumps({
        'id': video.id,
        'location': video.url,
        'path': video.host,
        'is_image_sequence': True if video.image_list else False,
        'annotated': video.annotation != '',
        'verified': video.verified,
        'rejected': video.rejected,
        'start_time': start_time,
        'end_time' : end_time,
        'turk_task' : full_video_task_data
    })

    label_data = []
    video_labels = video.labels.all()
    if len(video_labels):
        for v_label in video_labels:
            label_data.append({'name': v_label.name, 'color': v_label.color})
    else:
        for l in labels:
            label_data.append({'name': l.name, 'color': l.color})

    help_content = ''
    #if settings.HELP_URL and settings.HELP_USE_MARKDOWN:
    #    help_content = urllib.request.urlopen(settings.HELP_URL).read().decode('utf-8')
    #    help_content = markdown.markdown(help_content)

    response = render(request, 'video.html', context={
        'label_data': label_data,
        'video_data': video_data,
        'image_list': list(json.loads(video.image_list)) if video.image_list else 0,
        'image_list_path': video.host,
        'help_url': settings.HELP_URL,
        'help_embed': settings.HELP_EMBED,
        'mturk_data': mturk_data,
        'iframe_mode': mturk_data['authenticated'],
        'survey': False,
        'help_content': help_content
    })
    if not mturk_data['authenticated']:
        response['X-Frame-Options'] = 'SAMEORIGIN'
    return response


class AnnotationView(View):

    def get(self, request, video_id):
        video = Video.objects.get(id=video_id)
        return HttpResponse(video.annotation, content_type='application/json')

    def post(self, request, video_id):
        data = json.loads(request.body.decode('utf-8'))

        video = Video.objects.get(id=video_id)
        video.annotation = json.dumps(data['annotation'])
        video.save()

        hit_id = data.get('hitId', None)
        if hit_id != None:
            if not Task.valid_hit_id(hit_id):
                return HttpResponseForbidden('Not authenticated')
            else:
                try:
                    worker_id = data.get('workerId', '')
                    assignment_id = data.get('assignmentId', '')
                    task = Task.get_by_hit_id(hit_id)
                    task.complete(worker_id, assignment_id, data['metrics'])
                except ObjectDoesNotExist:
                    if not settings.DEBUG:
                        raise
        return HttpResponse('success')

class Populate(View):
    def get(self, request, video_id):
        video = Video.objects.get(id=video_id)
        if video is None:
            response_msg = "Your DB is broken!"
            return HttpResponse(response_msg, content_type='application/json')

        mp4_filename = video.filename
        if mp4_filename is None:
            response_msg = "Your did not configure the video filename yet!"
            return HttpResponse(response_msg, content_type='application/json')

        if len(mp4_filename) < 5:
            response_msg = "Your configured the video filename wrong, or you just left it empty!"
            return HttpResponse(response_msg, content_type='application/json')

        #/home/gemfield/BeaverDam/annotator
        current_dir = os.path.dirname(os.path.realpath(__file__))
        base_dir = os.path.abspath(os.path.join(current_dir, os.pardir))
        video_file = "%s/%s" %(base_dir, mp4_filename)
        base_video_file = os.path.basename(video_file)
        host_prefix = '/static/images/'
        img_dir = "%s%s" %(base_dir, host_prefix)

        if not os.path.isfile(video_file):
            response_msg = "could not find %s in the server !" %(video_file)
            return HttpResponse(response_msg, content_type='application/json')
        
        #opencv stuff
        video_cap = cv2.VideoCapture(video_file)
        video_fps = video_cap.get(cv2.CAP_PROP_FPS)
        video_width = int(video_cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        video_height = int(video_cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        video_frame_count = int(video_cap.get(cv2.CAP_PROP_FRAME_COUNT))
        if video_fps is None:
            response_msg = "Could not get the fps of video, may be video had a wrong format!"
            return HttpResponse(response_msg, content_type='application/json')

        if video_fps < 5:
            response_msg = "the fps of video is less than 5, may be video had a wrong format!"
            return HttpResponse(response_msg, content_type='application/json')

        if video_frame_count is None:
            response_msg = "Could not get the frame count of video, may be video had a wrong format!"
            return HttpResponse(response_msg, content_type='application/json')

        if video_frame_count < 5:
            response_msg = "the framecount of video is less than 5, may be video had a wrong format!"
            return HttpResponse(response_msg, content_type='application/json')

        #video_duration = video_frame_count/video_fps 
        #print("duration of %s: %d: fps %f" %(video_file, video_frame_count, video_fps))
        crop_path = '%s/%s/' %(img_dir, base_video_file)
        if not os.path.exists(crop_path):
            try:
                os.makedirs(crop_path)
            except Exception as e:
                response_msg = str(e)
                return HttpResponse(response_msg, content_type='application/json')

        frame_num = 0
        img_file_list = []
        while frame_num < video_frame_count:
            video_cap.set(cv2.CAP_PROP_POS_FRAMES, frame_num)
            got_frame, frame = video_cap.read()
            if not got_frame:
                if len(img_file_list) > 100:
                    frame_num = frame_num + 10
                    continue
                response_msg = "Error: get frame %d failed on %s!" %(frame_num, video_file)
                return HttpResponse(response_msg, content_type='application/json')

            crop_fname = "%s_%s_%s_%s_%s.jpg" %(str(video_width), str(video_height), str(video_frame_count), str(frame_num), str(video_fps))
            cv2.imwrite(crop_path + crop_fname, frame)

            frame_num = frame_num + 10
            img_file_list.append("%s%s/%s" %(host_prefix, base_video_file, crop_fname))

        video.image_list = json.dumps(img_file_list)
        video.save()
        data_header = "Total image number: %d\n" %(len(img_file_list))
        response_msg = data_header + video.image_list
        return HttpResponse(response_msg, content_type='application/json')

class ReceiveCommand(View):

    def post(self, request, video_id):
        data = json.loads(request.body.decode('utf-8'))

        try:
            vid_id = int(video_id)
            command_type = data['type']

            if 'bonus' in data:
                bonus = data['bonus']
            message = data['message']
            reopen = data['reopen']
            delete_boxes = data['deleteBoxes']
            block_worker = data['blockWorker']
            updated_annotations = json.dumps(data['updatedAnnotations'])

            if command_type == "accept":
                accept_video(request, vid_id, bonus, message, reopen, delete_boxes, block_worker, updated_annotations)
            elif command_type == "reject":
                reject_video(request, vid_id, message, reopen, delete_boxes, block_worker, updated_annotations)
            elif command_type == "email":
                email_worker(request, vid_id, data['subject'], message)

            return HttpResponse(status=200)
        except Exception as e:
            logger.exception(e)
            response = HttpResponse(status=500)
            response['error-message'] = str(e)
            return response
