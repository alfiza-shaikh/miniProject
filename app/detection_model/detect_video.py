import os
# comment out below line to enable tensorflow outputs
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
import tensorflow as tf
physical_devices = tf.config.experimental.list_physical_devices('GPU')
if len(physical_devices) > 0:
    tf.config.experimental.set_memory_growth(physical_devices[0], True)
from absl import app, flags, logging
from absl.flags import FLAGS
import detection_model.core.utils as utils
from detection_model.core.yolov4 import filter_boxes
from detection_model.core.functions import *
from tensorflow.python.saved_model import tag_constants
from PIL import Image
import cv2
import numpy as np
from tensorflow.compat.v1 import ConfigProto
from tensorflow.compat.v1 import InteractiveSession
import detection_model.detect_license_plate as detect_license_plate 
import time
from math import floor
import database.detectedvehiclesdb


# flags.DEFINE_string('framework', 'tf', '(tf, tflite, trt')
# flags.DEFINE_string('weights', './checkpoints/yolov4-416',
#                     'path to weights file')
# flags.DEFINE_integer('size', 416, 'resize images to')
# flags.DEFINE_boolean('tiny', False, 'yolo or yolo-tiny')
# flags.DEFINE_string('model', 'yolov4', 'yolov3 or yolov4')
# flags.DEFINE_string('video', './data/video/video.mp4', 'path to input video or set to 0 for webcam')
# flags.DEFINE_string('output', None, 'path to output video')
# flags.DEFINE_string('output_format', 'XVID', 'codec used in VideoWriter when saving video to file')
# flags.DEFINE_float('iou', 0.45, 'iou threshold')
# flags.DEFINE_float('score', 0.25, 'score threshold')# 0.50
# flags.DEFINE_boolean('count', False, 'count objects within video')
# flags.DEFINE_boolean('dont_show', False, 'dont show video output')
# flags.DEFINE_boolean('info', False, 'print info on detections')
# flags.DEFINE_boolean('crop', False, 'crop detections from images')
# flags.DEFINE_boolean('plate', False, 'perform license plate recognition')

def main(video_path):
    print("Detecting...")
    config = ConfigProto()
    config.gpu_options.allow_growth = True
    session = InteractiveSession(config=config)
    STRIDES, ANCHORS, NUM_CLASS, XYSCALE = utils.load_config("detection_model/data/classes/custom.names")
    input_size = 416
    # get video name by using split method
    video_name = video_path.split('/')[-1]
    video_name = video_name.split('.')[0]

    saved_model_loaded = tf.saved_model.load('detection_model/checkpoints/custom-416', tags=[tag_constants.SERVING])
    infer = saved_model_loaded.signatures['serving_default']
    saved_model_loaded1 = tf.saved_model.load('detection_model/checkpoints/custom_license_plate-416', tags=[tag_constants.SERVING])
    infer1 = saved_model_loaded1.signatures['serving_default']
    # begin video capture
    try:
        vid = cv2.VideoCapture(int(video_path))
        fps = vid.get(cv2.CAP_PROP_FPS)
    except:
        vid = cv2.VideoCapture(video_path)
        fps = vid.get(cv2.CAP_PROP_FPS)

    out = None

    frame_num = 0
    crop_rate = 10 #150 # capture images every so many frames (ex. crop photos every 150 frames)
    
    past_10_frame_plates = []

    while True:
        return_value, frame = vid.read()
        if return_value:
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frame_num += 1
            image = Image.fromarray(frame)
        else:
            print('Video has ended or failed, try a different video format!')
            break

        if frame_num % crop_rate == 0:  
            frame_size = frame.shape[:2]
            image_data = cv2.resize(frame, (input_size, input_size))
            image_data = image_data / 255.
            image_data = image_data[np.newaxis, ...].astype(np.float32)
            start_time = time.time()

            batch_data = tf.constant(image_data)
            pred_bbox = infer(batch_data)
            for key, value in pred_bbox.items():
                boxes = value[:, :, 0:4]
                pred_conf = value[:, :, 4:]

            boxes, scores, classes, valid_detections = tf.image.combined_non_max_suppression(
                boxes=tf.reshape(boxes, (tf.shape(boxes)[0], -1, 1, 4)),
                scores=tf.reshape(
                    pred_conf, (tf.shape(pred_conf)[0], -1, tf.shape(pred_conf)[-1])),
                max_output_size_per_class=50,
                max_total_size=50,
                iou_threshold= 0.45,
                score_threshold= 0.25
            )

            # format bounding boxes from normalized ymin, xmin, ymax, xmax ---> xmin, ymin, xmax, ymax
            original_h, original_w, _ = frame.shape
            bboxes = utils.format_boxes(boxes.numpy()[0], original_h, original_w)

            pred_bbox = [bboxes, scores.numpy()[0], classes.numpy()[0], valid_detections.numpy()[0]]

            # read in all class names from config
            class_names = utils.read_class_names(cfg.YOLO.CLASSES)

            # by default allow all classes in .names file
            allowed_classes = list(class_names.values())

            cropped_img_list = crop_objects(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB), pred_bbox, 'abc', allowed_classes)
            list_plate_num = []
            for img in cropped_img_list:
                #cv2.imshow('img', img[0])
                plate_number = detect_license_plate.main(img[0], infer1, True) 
                isexist = check_number_exist(past_10_frame_plates, plate_number)
                if not isexist and plate_number != '':
                    print( "License Plate Number ->" + plate_number +" Vehicle Type -> " + img[1] + "    Time in video : " + str(floor(frame_num/fps)))
                    list_plate_num.append(plate_number)
                    # Add vehicles to DB
                    video_ref=video_path.split("\\")[-1]
                    database.detectedvehiclesdb.insertDVDB(plate_number,img[1],video_ref,floor(frame_num/fps))
                    
            
            if len(past_10_frame_plates) > 10:
                past_10_frame_plates.pop(0)
            past_10_frame_plates.append(list_plate_num)

def check_number_exist(past_10_frame_plates, plate_number):
    for li in past_10_frame_plates:
        if plate_number in li:
            return True
    return False

if __name__ == '__main__':
    try:
        app.run(main('./data/video/video3.mp4'))
    except SystemExit:
        pass