import sqlite3
import json
import string
import cv2
import os
#import time

SQL_DB_NAME = 'db.sqlite3'
TABLE_NAME = 'annotator_video'
VIDEO_FIELD_NAME = 'filename'
LABEL_FIELD_NAME = 'annotation'
VIDEO_DIR = '/home/gemfield/video_annotation_web/'

COMPANY = 'mghy'
PROJECT = 'mgAI'
DATA_PHASE = 'Preprocessing'
DATA_TYPE = 'Video'
#DATA_TIME = time.strftime("%Y%m%d",time.localtime())


class AnnotationRecord():
    def __init__(self):
        self.hero_name = ''
        self.time = 0
        self.x = 0
        self.y = 0
        self.w = 0
        self.h = 0

# Fetch video_name & corresponding label_json_str
def fetchLabelJsonFromSqlite3():
    if not os.path.isfile(SQL_DB_NAME):
        raise Exception("cannot found %s in current filesystem" %SQL_DB_NAME)
        
    conn = sqlite3.connect(SQL_DB_NAME)
    cursor = conn.cursor()
    cursor.execute('select ' + VIDEO_FIELD_NAME + ',' + LABEL_FIELD_NAME + ' from ' + TABLE_NAME)
    raw_sql_records = cursor.fetchall()
    cursor.close()
    conn.close()
    return raw_sql_records

def parseJson(raw_str):
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
            annotation_record.hero_name = hero_name.encode('utf-8').strip()
            annotation_record.time = keyframe['frame']
            annotation_record.x = int(round(keyframe['x']))
            annotation_record.y = int(round(keyframe['y']))
            annotation_record.w = int(round(keyframe['w']))
            annotation_record.h = int(round(keyframe['h']))
            record_list.append(annotation_record)
    return record_list

def generateLabelImgs(filename, json_result):
    if not json_result:
        return
    if len(json_result) == 0:
        return
    # video file loaded by cv
    abs_filename = VIDEO_DIR + filename
    if not os.path.isfile(abs_filename):
        raise Exception("cannot found %s in current filesystem" %abs_filename)

    video_cap = cv2.VideoCapture(abs_filename)
    fps = video_cap.get(cv2.CAP_PROP_FPS)
    video_size = (int(video_cap.get(cv2.CAP_PROP_FRAME_WIDTH)), int(video_cap.get(cv2.CAP_PROP_FRAME_HEIGHT)))  
    print(abs_filename + '.txt')
    with open(abs_filename + '.txt', 'w') as f:
        for record in json_result:
            hero_time = int(round(record.time * 1000))
            hero_frame = int(round(record.time * fps))

            video_cap.set(cv2.CAP_PROP_POS_FRAMES, hero_frame)

            got_frame, frame = video_cap.read()
            if not got_frame:
                raise Exception("Error: get frame failed!")

            # cut the desired area
            #crop_img = frame[record.y : (record.y + record.h), record.x : (record.x + record.w)]
            crop_path = './annotation_output_big_pictures/'
            if not os.path.exists(crop_path):
                os.makedirs(crop_path)

            crop_fname = "%s_%s.jpeg" %( os.path.basename(abs_filename), str(hero_frame))
            print("Writing image " + crop_path + crop_fname)
            cv2.imwrite(crop_path + crop_fname, frame)

if __name__ == "__main__":
    raw_sql_result = fetchLabelJsonFromSqlite3()
    for (filename, json_str) in raw_sql_result:
        json_result = parseJson(json_str)
        #filename is /static/vidoes/wzry1.mp4
        generateLabelImgs(filename, json_result)

