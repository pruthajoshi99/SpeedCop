import cv2
import math
import random

def get_area(box, frame):
    return abs(box[2] - box[0]) * abs(box[3] - box[1]) / (frame.shape[0] * frame.shape[1])

def get_norm_area(box, width, height):
    xmin, xmax = box[1] / width, box[3] / width
    ymin, ymax = box[0] / height, box[2] / height
    area_norm = math.sqrt((xmax - xmin) * (ymax - ymin))
    center =  ((xmin + xmax) / 2, (ymin + ymax) / 2)
    
    return center, area_norm   

def calculate_speed(people, vehicles, frame, model_type):
    width, height = frame.shape[1], frame.shape[0]
    people_boxes, people_scores = [], []    
    if len(people) > 0:
        people_boxes, people_scores = zip(*people)

    vehicle_boxes, vehicle_scores = [], []
    if len(vehicles) > 0:
        vehicle_boxes, vehicle_scores = zip(*vehicles)

    people_distances, vehicle_distances = [], []
    people_weights, vehicle_weights = [], []

    for box, score in zip(people_boxes, people_scores):
        center, norm_area = get_norm_area(box, width, height)
        distance = 1 / norm_area

        horizontal_deviation = abs(center[0] - 0.5)
        # vertical_deviation = abs(center[1] - 0.5)

        horizontal_impact = 0.5 - horizontal_deviation
        horizontal_impact = math.sqrt(norm_area) * horizontal_impact

        weight = math.sqrt(norm_area) + horizontal_impact

        # text = str(round(math.sqrt(norm_area), 2)) + ', ' + str(round(horizontal_impact, 2)) + ' = ' + str(round(weight, 3))

        LOW, HIGH = 0.2, 0.65
        weight = min(max(weight - LOW, 0), HIGH - LOW) / (HIGH - LOW)

        green = math.floor(255 * (1 - weight))
        color = (255, green, 0)

        if get_area(box, frame) < 0.5:            
            frame = cv2.rectangle(frame, (box[1], box[0]), (box[3], box[2]), color, 6)
            # frame = cv2.putText(frame, str(round(weight, 2)) + ', ' + str(round(distance, 2)), (box[1] + 15, box[2] + 15), cv2.FONT_HERSHEY_SIMPLEX , 0.6, color, 1, cv2.LINE_AA)
            frame = cv2.putText(frame, str(round(distance, 1)) + 'm', (box[1] + 15, box[2] + 15), cv2.FONT_HERSHEY_SIMPLEX , 1, color, 1, cv2.LINE_AA)

            people_weights.append(weight)
            people_distances.append(distance)

    for box, score in zip(vehicle_boxes, vehicle_scores):
        center, norm_area = get_norm_area(box, width, height)
        distance = 1 / norm_area
        weight = math.sqrt(norm_area)

        frame = cv2.putText(frame, str(round(distance, 1)) + 'm', (box[1] + 16, box[2] + 20), cv2.FONT_HERSHEY_SIMPLEX , 1, (255, 0, 0), 1, cv2.LINE_AA)

        vehicle_weights.append(weight)
        vehicle_distances.append(distance)
    
    # people_min = 0 if len(people_distances) == 0 else min(people_distances)
    # vehicles_min = 0 if len(vehicle_distances) == 0 else min(vehicle_distances)
   
    # if people_min != 0 and vehicles_min != 0:
    #     distance = min(people_min, vehicles_min)
    # else:
    #     distance = max(people_min, vehicles_min)

    total_people_weights = sum(people_weights)
    total_vehicle_weights = sum(vehicle_weights)

    # print(total_people_weights)

    INITIAL_SPEED = 10 + 2 * random.random()
    speed_limit = INITIAL_SPEED
    if total_people_weights > 1:
        speed_limit = 15       # 15
        speed_limit -= 6 * total_people_weights
    else:
        speed_limit -= 12 * total_people_weights

    speed_limit -= 4 * total_vehicle_weights

    if model_type == 'ir':
        INITIAL_SPEED = 10 + 2 * random.random()
        speed_limit = INITIAL_SPEED
        if total_people_weights > 1:
            speed_limit = 15       # 15
            speed_limit -= 4 * total_people_weights     # 6
        else:
            speed_limit -= 4 * total_people_weights     # 12

        speed_limit -= 4 * total_vehicle_weights

    # if distance == 0:
    #     speed_limit = 15.5
    # else:
    #     speed_limit = 2.7 + (distance / 2.5) - 0.1 * (len(people_distances) + len(vehicle_distances))

    speed_limit = speed_limit if speed_limit < INITIAL_SPEED else INITIAL_SPEED
    speed_limit = speed_limit * 18 / 5
    speed_limit = max(speed_limit, random.randint(6, 9))   # in kmph
    # if speed_limit < 0:
    #     speed_limit = abs(speed_limit) / 2

    return frame, speed_limit