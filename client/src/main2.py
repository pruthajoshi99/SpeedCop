from gps_module import GPSModule
from server_comm import Server
from sound_alerts import SoundPlayback
from pipeline import Pipeline
from tqdm import tqdm
from queue import Queue
import time
import glob
import numpy as np
import cv2
import threading
import time

# model_path = 'models/ssdlite_mobilenet_v2_custom_2020_07_25_60k/frozen_inference_graph.pb'
# threshold = 0.2
cap = cv2.VideoCapture('videos/mumbai.mp4')
save_video = True
show_video = True

shape = (int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)), int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)))
fps = cap.get(cv2.CAP_PROP_FPS)
total_frames = cap.get(cv2.CAP_PROP_FRAME_COUNT)
current_frame = 0

video_length = int(total_frames / fps)    # in seconds

timings = [
    # ((1, 35), (5, 55)),
    # ((1, 58), (5, 55)),
    # ((0, 54), (1, 11)),
    # ((1, 19), (2, 19)),
    # ((4, 15), (4, 41))
    ((1, 19), (12, 0))
]

# model_type = 'ir'
model_type = 'normal'

if save_video:
    if model_type == 'ir':
        out = cv2.VideoWriter('temp.mp4', cv2.VideoWriter_fourcc(*'MJPG'), 30, (640, 480))
    else:
        out = cv2.VideoWriter('temp.mp4', cv2.VideoWriter_fourcc(*'MJPG'), fps, shape)

gps_module = GPSModule()
server_comm = Server()
sound_alert = SoundPlayback(Queue())

if model_type == 'ir':
    model_path = '/home/adwait_bhope/Desktop/Files/Hackathons/Smart India Hackathon Software 19-20/code/rpi/models/ssdlite_mobilenet_v2_custom_ir_2020_08_01_52k/frozen_inference_graph.pb'
else:
    model_path = '/home/adwait_bhope/Desktop/Files/Hackathons/Smart India Hackathon Software 19-20/code/rpi/models/ssdlite_mobilenet_v2_custom_2020_07_25_60k/frozen_inference_graph.pb'

pipeline = Pipeline(model_path, model_type)
last_speed_limit = ''
last_speed_sign, last_speed_sign_frame_count = None, 0

file='server_response.txt' 
with open(file, 'w') as filetowrite:
    filetowrite.write('')

while True:
    ret, frame = cap.read()
    current_frame += 1

    if not ret:
        break

# for image_path in tqdm(sorted(glob.glob('/home/adwait_bhope/Desktop/Files/Hackathons/Smart India Hackathon Software 19-20/utils/IR Pedestrians/CVC 09 Infrared/DayTime/Test/FramesPos/*.png'))):
#     # image_id = os.path.splitext(os.path.split(image_path)[-1])[0]
#     frame = cv2.imread(image_path)

    # if current_frame % 4 != 0:
        # continue
    
    current_time = video_length * current_frame / total_frames
    process = False if len(timings) > 0 else True
    end = False

    # print(f'{int((current_time // 60))}m {round(current_time % 60, 2)}s')

    for time_segment in timings:
        start_time = time_segment[0][0] * 60 + time_segment[0][1]
        end_time = time_segment[1][0] * 60 + time_segment[1][1]
        
        if start_time < current_time < end_time:
            process = True
        if current_time > end_time:
            end = True

    if end:
        break

    if not process:
        continue

    lat, lng, current_speed, vehicle_number = gps_module.get_data()
    
    # frame = cv2.resize(img, (480, 270))
    
    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    frame, speed_limit, sign_speed = pipeline.process_frame(frame, last_speed_sign)

    if sign_speed and last_speed_sign != sign_speed:
        last_speed_sign = sign_speed
        last_speed_sign_frame_count = -1
    
    last_speed_sign_frame_count += 1
    if last_speed_sign_frame_count > 200:
        last_speed_sign = None

    last_displayed_speed_int = int(last_speed_limit) if last_speed_limit != '' else 0
    speed_limit, accident_zone = server_comm.add_data(lat, lng, vehicle_number, current_speed, speed_limit, last_displayed_speed_int)
    if speed_limit:
        last_speed_limit = str(round(speed_limit))

    if accident_zone:
        sound_alert.queue.put('sounds/accident_zone.wav')

    frame = cv2.putText(frame, last_speed_limit, (20, 90), cv2.FONT_HERSHEY_SIMPLEX , 3, (255, 0, 0), 2, cv2.LINE_AA)    

    frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)

    if save_video:
        out.write(frame.astype('uint8'))
    
    if show_video:
        cv2.imshow("preview", frame)
    
    key = cv2.waitKey(1)
    if key & 0xFF == ord('q'):
        break

    # time.sleep(0.3)

if save_video:
    out.release()
    

