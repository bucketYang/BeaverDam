import sqlite3
import json
import string
import cv2
import os
import sys

SQL_DB_NAME = 'db.sqlite3'
VIDEO_DIR = '/home/gemfield/video_annotation_web/'

class AnnotationRecord():
    def __init__(self):
        self.hero_name = ''
        self.time = 0
        self.x = 0
        self.y = 0
        self.w = 0
        self.h = 0

# Fetch video_name & corresponding label_json_str
def FetchLabelJson(id):
    conn = sqlite3.connect(SQL_DB_NAME)
    suffix_condition = "where id=%s" %(id)
    if id == 'all':
        suffix_condition = ''
    cursor = conn.cursor()
    cursor.execute('select filename,annotation,image_list from annotator_video %s' %(suffix_condition))
    raw_sql_records = cursor.fetchall()
    cursor.close()
    conn.close()
    return raw_sql_records

def ParseJson(raw_str):
    record_list = []
    #invalid json
    if len(raw_str) < 10 :
        return record_list
    #json_res will be a list
    json_res = json.loads(raw_str)
    for annotation in json_res:
        hero_name = annotation['type']
        keyframes = annotation["keyframes"]
        for keyframe in keyframes:
            annotation_record = AnnotationRecord()
            annotation_record.hero_name = hero_name
            annotation_record.time = keyframe['frame']
            annotation_record.x = int(round(keyframe['x']))
            annotation_record.y = int(round(keyframe['y']))
            annotation_record.w = int(round(keyframe['w']))
            annotation_record.h = int(round(keyframe['h']))
            record_list.append(annotation_record)
    return record_list

def GenerateLabelImgs(filename, json_result, is_image_list):
    if not is_image_list:
        return
    
    first_frame = 0
    if not json_result:
        return
    if len(json_result) == 0:
        return
    # video file loaded by cv
    abs_filename = VIDEO_DIR + filename
    if not os.path.isfile(abs_filename):
        print ("cannot found %s in current filesystem" %abs_filename)
        return

    base_filename = os.path.basename(abs_filename)

    video_cap = cv2.VideoCapture(abs_filename)
    fps = video_cap.get(cv2.CAP_PROP_FPS)
    video_size = (int(video_cap.get(cv2.CAP_PROP_FRAME_WIDTH)), int(video_cap.get(cv2.CAP_PROP_FRAME_HEIGHT))) 
    frame_count = video_cap.get(cv2.CAP_PROP_FRAME_COUNT) 
    video_duration = frame_count/fps 
    print("duration of %s: %d: fps %f" %(abs_filename, frame_count, fps))
    for record in json_result:
        #we got 1 frame in 10 frames
        hero_frame = record.time * 10
        video_cap.set(cv2.CAP_PROP_POS_FRAMES, hero_frame)

        got_frame, frame = video_cap.read()
        if not got_frame:
            print("Error: get frame %d failed on %s!" %(hero_frame, abs_filename))
            continue
        # cut the desired area
        crop_img = frame[record.y : (record.y + record.h), record.x : (record.x + record.w)]
        #crop_img = cv2.rectangle(frame, (record.x, record.y), (record.x + record.w, record.y + record.h), (255,0,0))
        crop_path = './annotation_output/%s/' %(record.hero_name.encode('utf-8').strip())
        if not os.path.exists(crop_path):
            os.makedirs(crop_path)

        print(hero_frame, record.x, record.y, record.w, record.h)
        crop_fname = "%s_%s_%s_%s_%s_%s.jpg" %(base_filename.encode('utf-8').strip(), str(hero_frame), str(record.x), str(record.y), str(record.w),  str(record.h))
        print('imwrite: ',crop_path + crop_fname)
        cv2.imwrite(crop_path + crop_fname, crop_img)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: %s <id>" %(sys.argv[0]))
        sys.exit(1)

    id = sys.argv[1]

    raw_sql_result = FetchLabelJson(id)
    for (filename, json_str, image_list) in raw_sql_result:
        is_image_list = False
        if len(image_list) > 100:
            is_image_list = True
        json_result = ParseJson(json_str)
        #filename is /static/vidoes/wzry1.mp4
        GenerateLabelImgs(filename, json_result, is_image_list)

