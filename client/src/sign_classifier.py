import os
import cv2
import numpy as np
from tensorflow.keras.preprocessing import image
from tensorflow.keras.models import load_model

sign_categories = ['compulsory', 'warning', 'other']
num_class = len(sign_categories)
img_size = 96

model = load_model('models/sign_classifier/saved_model.h5')

def detect_category(red_mask):
    # TODO: remove writing to disk and reading from it
    path = 'mask.png'
    cv2.imwrite(path, red_mask)

    # load imamge into a 4D Tensor, convert it to a numpy array and expand to 4 dim
    img = image.load_img(path, target_size = (img_size, img_size), color_mode='grayscale')
    image_tensor = image.img_to_array(img)

    image_tensor = image_tensor / 255
    image_tensor = np.expand_dims(image_tensor, axis=0)

    # run model to get predictions
    pred = model.predict(image_tensor)
    pred = np.argmax(pred)
    prediction = sign_categories[pred]

    os.remove(path)
    return prediction