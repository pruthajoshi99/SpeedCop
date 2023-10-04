from threading import Thread, Lock
from queue import Queue, Empty
from math import ceil, floor
import os
import time
import json
import random
import requests
import statistics

class MyThread(Thread):

    def __init__(self, queue, response_queue, args=(), kwargs=None):
        Thread.__init__(self, args=(), kwargs=None)
        self.queue = queue
        self.response_queue = response_queue
        self.daemon = True

    
    def send_data_to_server(self, params):
        data = {}
        data['lat'] = params[0]
        data['lng'] = params[1]
        data['speed'] = floor(params[2])    # current_email
        data['speed_by_vr'] = ceil(params[3])
        data['vehicle_no'] = params[4]
        data['left_sum'] = 20
        data['left_count'] = 3
        data['right_sum'] = 21
        data['right_count'] = 4
        
        speed = data['speed_by_vr']
        accident_zone = False
        try:
            print('sending request')
            response = requests.post('https://speedcop.herokuapp.com/backend/speed/reportspeed', data)
            # print(response.text)
            speeds = json.loads(response.text.replace('\'', '"'))
            speed = speeds['reccomended_speed']
            # accident_zone = speeds['accident_prone_area']
        except ConnectionError:
            print('connection error')
        except JSONDecodeError:
            print('json error')
            
        # os.system('cls') if os.name == 'nt' else os.system('clear')
        # print('VR speed:', data['speed_by_vr'], 'kmph')
        print('Server recommendation:', floor(speed), 'kmph\n')
        self.response_queue.put((speed, accident_zone))

    def run(self):
        while True:
            self.send_data_to_server(self.queue.get())


class Server:
    
    def __init__(self):
        self.thread = MyThread(Queue(), Queue(), args=())
        self.thread.start()
        self.count = 1
        self.lat_sum = 0
        self.lng_sum = 0
        self.current_speed_sum = 0
        self.speed_by_recog_sum = []
        self.interval = 15       # send data to server after every x frames processed
        
        
    def add_data(self, lat, lng, vehicle_number, current_speed, speed_by_recog, last_displayed_speed):
        if self.count % (self.interval + 1) != 0:
            self.lat_sum += lat
            self.lng_sum += lng
            self.current_speed_sum += current_speed
            self.speed_by_recog_sum.append(speed_by_recog)
            
            if len(self.speed_by_recog_sum) > self.interval:
                self.speed_by_recog_sum.pop(0)

            self.count += 1
            return None, False
        
        else:
            lat = self.lat_sum / self.interval
            lng = self.lng_sum / self.interval
            self.speed_by_recog_sum.append(speed_by_recog)
            
            if len(self.speed_by_recog_sum) > self.interval:
                self.speed_by_recog_sum.pop(0)

            current_speed = self.current_speed_sum / self.interval

            speeds_list = self.speed_by_recog_sum.copy()
            # last_speed = statistics.mean(speeds_list[-3:])

            speeds_list.sort()
            median_50 = statistics.median(self.speed_by_recog_sum)
            if median_50 > last_displayed_speed and last_displayed_speed != 0:
                difference = median_50 - last_displayed_speed
                difference = min(difference, random.randint(3, 6))
                speed_by_recog = last_displayed_speed + difference
                # speed_by_recog = speeds_list[round(0.25 * self.interval)]
            else:
                # speed_by_recog = speeds_list[round(0.75 * self.interval)]
                # print(round(speed_by_recog), end=', ')
                speed_by_recog = statistics.median(self.speed_by_recog_sum)
                # print(round(speed_by_recog))
            # speed_by_recog = statistics.median(self.speed_by_recog_sum)

            if self.count % 60 == 0:        
                self.thread.queue.put((lat, lng, current_speed, speed_by_recog, vehicle_number))
            
            accident_zone = False
            try:
                speed_from_server, accident_zone = self.thread.response_queue.get(block=False)
                with open('server_response.txt', 'a+') as server_response_file:
                    server_response_file.write('Speed from server: ' + str(round(speed_from_server)) + 'km/h\n\n')

                # if speed_by_recog > speed_from_server + 10:
                #     speed_by_recog -= 5
                # else:
                #     speed_by_recog = speed_from_server
            except Empty:
                pass

            self.lat_sum, self.lng_sum, self.current_speed_sum = 0, 0, 0
            
            self.count += 1
            return speed_by_recog, accident_zone

