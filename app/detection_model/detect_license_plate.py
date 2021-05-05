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

def main(image,infer, read_plate):
    config = ConfigProto()
    config.gpu_options.allow_growth = True

    STRIDES, ANCHORS, NUM_CLASS, XYSCALE = utils.load_config( "detection_model/data/classes/custom_license_plate.names")

    input_size = 416
    
    original_image = image
    original_image = cv2.cvtColor(original_image, cv2.COLOR_BGR2RGB)

    image_data = cv2.resize(original_image, (input_size, input_size))
    image_data = image_data / 255.

    images_data = []
    for i in range(1):
        images_data.append(image_data)
    images_data = np.asarray(images_data).astype(np.float32)
    
    batch_data = tf.constant(images_data)
    pred_bbox = infer(batch_data)
    for key, value in pred_bbox.items():
        boxes = value[:, :, 0:4]
        pred_conf = value[:, :, 4:]

    # run non max suppression on detections
    boxes, scores, classes, valid_detections = tf.image.combined_non_max_suppression(
        boxes=tf.reshape(boxes, (tf.shape(boxes)[0], -1, 1, 4)),
        scores=tf.reshape(
            pred_conf, (tf.shape(pred_conf)[0], -1, tf.shape(pred_conf)[-1])),
        max_output_size_per_class=50,
        max_total_size=50,
        iou_threshold=0.45,
        score_threshold=0.5
    )

    # format bounding boxes from normalized ymin, xmin, ymax, xmax ---> xmin, ymin, xmax, ymax
    original_h, original_w, _ = original_image.shape
    bboxes = utils.format_boxes(boxes.numpy()[0], original_h, original_w)
    
    # hold all detection data in one variable
    pred_bbox = [bboxes, scores.numpy()[0], classes.numpy()[0], valid_detections.numpy()[0]]

    # read in all class names from config
    class_names = utils.read_class_names("detection_model/data/classes/custom_license_plate.names")

    # by default allow all classes in .names file
    allowed_classes = list(class_names.values())

    image, plate_number = utils.draw_bbox(original_image, pred_bbox, False, allowed_classes=allowed_classes, read_plate = read_plate)
    
    image = Image.fromarray(image.astype(np.uint8))
    image = cv2.cvtColor(np.array(image), cv2.COLOR_BGR2RGB)
    return plate_number

if __name__ == '__main__':
    try:
        img = cv2.imread('data/images/car2.jpg')
        #app.run(main(img, True))
        saved_model_loaded = tf.saved_model.load('./checkpoints/custom_license_plate-416', tags=[tag_constants.SERVING])
        infer = saved_model_loaded.signatures['serving_default']
        plate_number = main(img,infer, True)
    except SystemExit:
        pass
