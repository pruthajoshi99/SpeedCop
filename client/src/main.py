from gps_module import GPSModule
from server_comm import Server
import numpy as np
import cv2
import threading
import time

model_path = 'models/ssdlite_mobilenet_v2_custom_2020_07_25_60k/frozen_inference_graph.pb'
threshold = 0.2
cap = cv2.VideoCapture('videos/mumbai.mp4')
save_video = False
show_video = True

frame_no = 0

if save_video:
    out = cv2.VideoWriter('output.avi', cv2.VideoWriter_fourcc(*'MJPG'), 15., (480, 270))

gps_module = GPSModule()
server_comm = Server()

while True:
    r, img = cap.read()
    frame_no += 1

#    if frame_no % 4 != 0:
#        continue
        
    lat, lng, current_speed = gps_module.get_data()
    
    # img = cv2.resize(img, (480, 270))
    boxes, scores, classes, num = odapi.processFrame(img)   

    people = [1]
    vehicles = [2, 3, 4, 6, 7, 8]
    street_signs = [10, 12, 13]
    
    people = [5]
    vehicles = [1, 2, 3, 4, 7]
    street_signs = [6]
    
    people_boxes = []
    vehicle_boxes = []
    
    for i, box in enumerate(boxes):
        if classes[i] in people and scores[i] > threshold:
            cv2.rectangle(img, (box[1], box[0]), (box[3], box[2]), (255, 0, 0), 2)
            distance = 20000 / abs((box[1] - box[3]) * (box[0] - box[2]))
            people_boxes.append(distance)
        elif classes[i] in vehicles and scores[i] > threshold:
            cv2.rectangle(img, (box[1], box[0]), (box[3], box[2]), (0, 255, 0), 2)
            distance = 36000 / abs((box[1] - box[3]) * (box[0] - box[2]))
            vehicle_boxes.append(distance)
        elif classes[i] in street_signs and scores[i] > threshold:
            cv2.rectangle(img, (box[1], box[0]), (box[3], box[2]), (0, 0, 255), 2)
    
    people_min = 0 if len(people_boxes) == 0 else min(people_boxes)
    vehicles_min = 0 if len(vehicle_boxes) == 0 else min(vehicle_boxes)
    
    if people_min != 0 and vehicles_min != 0:
        distance = min(people_min, vehicles_min)
    else:
        distance = max(people_min, vehicles_min)
        
    if distance == 0:
        speed_limit = 15.5
    else:
        speed_limit = 2.7 + (distance / 2.5) - 0.1 * (len(people_boxes) + len(vehicle_boxes))

    speed_limit = speed_limit if speed_limit < 15.5 else 15.5 
    speed_limit = speed_limit * 18 / 5
    if speed_limit < 0:
        speed_limit = abs(speed_limit) / 2
    server_comm.add_data(lat, lng, current_speed, speed_limit)
    
    if save_video:
        out.write(img.astype('uint8'))
    
    if show_video:
        cv2.imshow("preview", img)
    
    key = cv2.waitKey(1)
    if key & 0xFF == ord('q'):
        break

if save_video:
    out.release()
    

