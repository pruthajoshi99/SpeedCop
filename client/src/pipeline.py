import cv2
import numpy as np
import speed_detector
import sign_classifier
from object_detector import DetectorAPI
from speed_calculation import calculate_speed

class Pipeline:

    def __init__(self, path, model_type):
        self.model = DetectorAPI(path)
        self.threshold = 0.40
        self.model_type = model_type

        if model_type == 'ir':
            self.categories = {
                'person': [1],
                'vehicle': [],
                'traffic sign': []
            }

        else:
            self.categories = {
                'person': [5],
                'vehicle': [1, 2, 3, 4, 7],
                'traffic sign': [6]
            }

        self.main_colors = {
            'person': (0, 0, 255),
            'vehicle': (0, 128, 0),
            'traffic sign': (0, 0, 255)
        }

        self.red_mask = (
            np.array([20, 130, 115]),
            np.array([100, 190, 135]),
        )       

    def get_iou(self, box1, box2):
        '''
        Returns IOU (intersection / union) for bounding boxes of box1 and box2.
        This can be used to eliminate multiple overlapping boxes for the same object.
        '''

        area1 = (box1[3] - box1[1]) * (box1[2] - box1[0])
        area2 = (box2[3] - box2[1]) * (box2[2] - box2[0])

        # calculate coordinates of overlapping area
        xmin = max(box1[1], box2[1])
        ymin = max(box1[0], box2[0])
        xmax = min(box1[3], box2[3])
        ymax = min(box1[2], box2[2])

        if xmin > xmax or ymin > ymax:
            return area1, area2, 0

        intersection = max((xmax - xmin) * (ymax - ymin), 0)
        union = area1 + area2 - intersection
        return area1, area2, intersection / union

    def non_max_suppression(self, boxes_scores):
        boxes, scores = boxes_scores
        eliminations = [False] * len(boxes)

        for box1, score1 in zip(boxes, scores):
            for box2, score2 in zip(boxes, scores):
                if box1 is not box2:
                    area1, area2, iou = self.get_iou(box1, box2)
                    if iou > 0.25:
                        if area1 > area2:
                            eliminations[boxes.index(box2)] = True
                        else:
                            eliminations[boxes.index(box1)] = True

        return [(box, scores[boxes.index(box)]) for box, eliminated in zip(boxes, eliminations) if not eliminated]

    def get_area(self, box, frame):
        return abs(box[2] - box[0]) * abs(box[3] - box[1]) / (frame.shape[0] * frame.shape[1])

    def segregate_detections(self, boxes, scores, classes):
        people = ([], [])
        vehicles = ([], [])
        traffic_signs = ([], [])
        
        for box, score, classs in zip(boxes, scores, classes):
            if score > self.threshold and classs in self.categories['person']:
                people[0].append(box)
                people[1].append(score)
            elif score > self.threshold and classs in self.categories['vehicle']:
                vehicles[0].append(box)
                vehicles[1].append(score)
            elif score > self.threshold and classs in self.categories['traffic sign']:
                traffic_signs[0].append(box)
                traffic_signs[1].append(score)

        return people, vehicles, traffic_signs

    def draw_boxes(self, boxes_scores, frame, label):
        if len(boxes_scores) == 0:
            return frame
        
        boxes, scores = zip(*boxes_scores)
        for box, score in zip(boxes, scores):
            if self.get_area(box, frame) < 0.5:
                frame = cv2.rectangle(frame, (box[1], box[0]), (box[3], box[2]), self.main_colors[label], 6)

                # label on top left corner of box
                # frame = cv2.putText(frame, label, (box[1] + 2, box[0] + 15), cv2.FONT_HERSHEY_SIMPLEX , 0.6, self.main_colors[label], 1, cv2.LINE_AA)
                
                # score below the label
                # frame = cv2.putText(frame, f'score: {score:.2f}', (box[1] + 2, box[0] + 30), cv2.FONT_HERSHEY_SIMPLEX , 0.4, self.main_colors[label], 1, cv2.LINE_AA)
        
        return frame

    def check_traffic_sign(self, sign_box, frame):
        cropped_sign = frame[sign_box[0]:sign_box[2], sign_box[1]:sign_box[3]]
        cropped_sign_ycb = cv2.cvtColor(cropped_sign, cv2.COLOR_RGB2YCrCb)
        red_mask = cv2.inRange(cropped_sign_ycb, self.red_mask[0], self.red_mask[1])

        area_ok = self.get_area(sign_box, frame) < 0.2
        return area_ok, cv2.countNonZero(red_mask) > 200, cropped_sign, red_mask

    def process_traffic_signs(self, traffic_signs, frame):
        speed = None

        if len(traffic_signs) == 0:
            return frame, speed

        boxes, scores = zip(*traffic_signs)
        for box, score in zip(boxes, scores):
            area_ok, is_valid, cropped_sign, red_mask = self.check_traffic_sign(box, frame)
            
            if area_ok and is_valid:
                speed = speed_detector.run(cropped_sign)
                category = sign_classifier.detect_category(red_mask)

                frame = cv2.rectangle(frame, (box[1], box[0]), (box[3], box[2]), self.main_colors['traffic sign'], 6)

                if speed is not None:
                    frame = cv2.putText(frame, 'Speed: ' + str(speed), (box[1] + 6, box[2] + 30), cv2.FONT_HERSHEY_SIMPLEX , 1, self.main_colors['traffic sign'], 2, cv2.LINE_AA)
                else:
                    frame = cv2.putText(frame, str(category), (box[1] + 6, box[2] + 30), cv2.FONT_HERSHEY_SIMPLEX , 1, self.main_colors['traffic sign'], 2, cv2.LINE_AA)

                # label on top left corner of box
                # frame = cv2.putText(frame, 'traffic sign', (box[1] + 2, box[0] + 15), cv2.FONT_HERSHEY_SIMPLEX , 0.6, colors['traffic sign'], 1, cv2.LINE_AA)
                
                # score below the label
                # frame = cv2.putText(frame, f'score: {score:.2f}', (box[1] + 2, box[0] + 30), cv2.FONT_HERSHEY_SIMPLEX , 0.4, colors['traffic sign'], 1, cv2.LINE_AA)

        return frame, speed

    def calculate_speed_limit(self, people, vehicles, sign_speed, frame, last_sign_speed):
        frame, speed_limit = calculate_speed(people, vehicles, frame, self.model_type)
    
        if sign_speed and speed_limit > sign_speed:
            speed_limit = sign_speed
        elif last_sign_speed and speed_limit > last_sign_speed:
            speed_limit = last_sign_speed

        # frame = cv2.putText(frame, str(round(speed_limit)), (20, 90), cv2.FONT_HERSHEY_SIMPLEX , 3, (255, 0, 0), 2, cv2.LINE_AA)
        return frame, speed_limit

    def process_frame(self, frame, last_sign_speed):
        '''
        frame: np.ndarray with RGB color format
        '''

        # run inference through main model
        boxes, scores, classes, _ = self.model.process_frame(frame)
        people, vehicles, traffic_signs = self.segregate_detections(boxes, scores, classes)

        # use NMS to remove overalapping objects
        # keeps box with higher confidence for boxes which have an IOU > 0.5
        people = self.non_max_suppression(people)
        vehicles = self.non_max_suppression(vehicles)
        traffic_signs = self.non_max_suppression(traffic_signs)

        # speed_limit = 80
        frame, sign_speed = self.process_traffic_signs(traffic_signs, frame)
        frame, speed_limit = self.calculate_speed_limit(people, vehicles, sign_speed, frame, last_sign_speed)

        # draw bounding boxes over vehicles and pedestrians
        # frame = self.draw_boxes(people, frame, 'person')
        frame = self.draw_boxes(vehicles, frame, 'vehicle')

        return frame, speed_limit, sign_speed
