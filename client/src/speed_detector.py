#-*- coding: utf-8 -*-
import cv2
import time
import glob
import numpy as np
import keras.models

import digit_detector.region_proposal as rp
import digit_detector.show as show
import digit_detector.detect as detector
import digit_detector.file_io as file_io
import digit_detector.preprocess as preproc
import digit_detector.classify as cls

detect_model = "models/digit_recognition/detector_model.hdf5"
recognize_model = "models/digit_recognition/recognize_model.hdf5"

mean_value_for_detector = 107.524
mean_value_for_recognizer = 112.833

model_input_shape = (32,32,1)
# DIR = 'tests/imgs'

preproc_for_detector = preproc.GrayImgPreprocessor(mean_value_for_detector)
preproc_for_recognizer = preproc.GrayImgPreprocessor(mean_value_for_recognizer)

char_detector = cls.CnnClassifier(detect_model, preproc_for_detector, model_input_shape)
char_recognizer = cls.CnnClassifier(recognize_model, preproc_for_recognizer, model_input_shape)

digit_spotter = detector.DigitSpotter(char_detector, char_recognizer, rp.MserRegionProposer())

if __name__ == "__main__":
#    img_files = file_io.list_files(directory=DIR, pattern="*.png", recursive_option=False, n_files_to_sample=None, random_order=False)
    img_files = sorted(glob.glob('images/*.png'))
    img_files = ['images/50.png', 'images/80.png']
    
    for img_file in img_files[0:]:
        img = cv2.imread(img_file)
        speed = run(img)
        print(img_file, ':',speed)
        
    print()


def detect_speed(frame):
    speed, bbs, probs = digit_spotter.run(frame, threshold=0.5, do_nms=True, nms_threshold=0.1)
    
    if not speed:
        return None
    
    x1s = [bbox[2] for bbox in bbs]
    digits = sorted(zip(x1s, speed))
    _, digits = zip(*digits)

    first_digit = None
    for digit in digits:
        if first_digit and (digit == '5' or digit == '0'):
            speed = (first_digit * 10) + int(digit)
        else:
            first_digit = int(digit)

    if isinstance(speed, int):
        return speed

    return None


def run(frame):
    if frame is None:
        return None
    
    start = time.time()
    speed = detect_speed(frame)
    end = time.time()    
    # print(f'Time required: {round(end - start, 2)}s')

    return speed




