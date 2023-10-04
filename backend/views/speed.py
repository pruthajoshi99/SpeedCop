from os import times
from speedcop.settings import EMAIL_HOST_USER
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.mail import send_mail

import os
import pymongo
from datetime import datetime, timedelta, tzinfo
import pytz

from . import reverse_geocoding
from . import nearbyvehicles, nearbyplaces, accidents
from speedcop.settings import EMAIL_HOST_USER
from statistics import mean, median

client = pymongo.MongoClient(os.environ["SPEEDCOP_DATABASE"])

database = client.sihdatabase


@csrf_exempt
def report_speed(request):
    vehicle_no = request.POST['vehicle_no']
    lat = float(request.POST['lat'])
    lng = float(request.POST['lng'])
    speed = int(request.POST['speed'])
    speed_by_vr = int(request.POST['speed_by_vr'])

    timestamp = datetime.now(pytz.timezone('Asia/Kolkata'))
    response = {}

    data = reverse_geocoding.get_location(lat, lng)
    city = data['features'][0]['properties']['address']['state_district'].split()[
        0]
    area = data['features'][0]['properties']['display_name'].split(',')[0]
    try:
        road = data['features'][0]['properties']['address']['road']
    except Exception as e:
        # If Road name not found
        print(e)
        road = "Unknown"

    # Calculate direction of vehicle
    direction = 0
    try:
        # Get the latest speed entry of that vehicle
        speeds = database.speed.find({"vehicle_no": vehicle_no}).sort([
            ("$natural", -1)]).limit(1)
        for s in speeds:
            new_lat, new_lng = s['lat'], s['lng']
            direction = nearbyvehicles.get_vehicle_direction(
                lat, lng, new_lat, new_lng)
            print("Direction=> ", direction)
    except pymongo.errors.OperationFailure as e:
        print(e)

    response['accident_count'] = accidents.count_accident()
    response['vehicle_list'] = nearbyvehicles.get_nearby_vehicles_speed(
        lat, lng, road, direction)
    response['nearby_places'] = nearbyplaces.get_nearby_places(str(lat),str(lng))
    near_by_places = response['nearby_places']

    distance = []
    for s in near_by_places['schools']:
        distance.append(s['distance'])
    
    for h in near_by_places['hospitals']:
        
        distance.append(h['distance'])
    
   
    distance.sort()
    if distance is None:
        closet_distance = 0
    else:
        closet_distance = distance[0]

    speed_limit = get_speed_limit(lat, lng, road, direction,speed_by_vr,closet_distance)
    response['reccomended_speed'] = speed_limit

    # print(vehicle_no, speed, speed_limit)
    if speed > speed_limit:
        # Enter data in 'Violations' collection
        try:
            time = timestamp - timedelta(minutes=30)
            database.buffer_violations.delete_one(
                {"$and": [{"vehicle_no": vehicle_no}, {"timestamp": {"$lte": time}}]})
            query = {"$and": [{"vehicle_no": vehicle_no},
                              {"timestamp": {"$gt": time}}]}
            vehicle = database.buffer_violations.find_one(query)
            user = database.vehicles.find_one({"vehicle_no": vehicle_no})
            if vehicle:
                print("Data already in buffer")
                tz_info = vehicle['latest_timestamp'].tzinfo
                if (timestamp.now(tz_info) - vehicle['latest_timestamp']).seconds >= 10:
                    print((timestamp.now(tz_info) - vehicle['latest_timestamp']).seconds)
                    if vehicle['Count'] < 30:
                        print("Do not add to violations")
                        if vehicle['speed'] > speed:
                            print("increment count")
                            database.buffer_violations.update_one(
                                query, {"$set": {"latest_timestamp": timestamp}, "$inc": {"Count": 1}})
                            response['success'] = True
                        else:
                            print("increment count and update document")
                            database.buffer_violations.update_one(query, {"$set": {
                                "name": user['name'],
                                "vehicle_no": vehicle_no,
                                "lat": lat,
                                "lng": lng,
                                "speed": speed,
                                "speedlimit": speed_limit,
                                "difference": speed - speed_limit,
                                "latest_timestamp": timestamp,
                                "City": city,
                                "Area": area,
                                "Paid": False,
                            },
                                "$inc": {"Count": 1}})
                            response['success'] = True
                    else:
                        print("Violated")
                        database.buffer_violations.delete_one(query)
                        send_mail("Violation of speed", "You receiving this email for the violation of rules setup by SpeedCop.", EMAIL_HOST_USER, [
                                  user['email'], ], fail_silently=False)
                        if vehicle['speed'] > speed:
                            vehicle.pop('latest_timestamp')
                            database.violations.insert(vehicle)
                        else:
                            database.violations.insert({
                                "name": user['name'],
                                "vehicle_no": vehicle_no,
                                "lat": lat,
                                "lng": lng,
                                "speed": speed,
                                "speedlimit": speed_limit,
                                "difference": speed - speed_limit,
                                "timestamp": timestamp,
                                "latest_timestamp": timestamp,
                                "City": city,
                                "Area": area,
                                "Paid": False,
                            })
                        response['success'] = True
                else:
                    print("Violated to early")
            else:
                print("Data not in buffer. Adding!")
                try:
                    database.buffer_violations.insert({
                        "name": user['name'],
                        "vehicle_no": vehicle_no,
                        "lat": lat,
                        "lng": lng,
                        "speed": speed,
                        "speedlimit": speed_limit,
                        "difference": speed - speed_limit,
                        "timestamp": timestamp,
                        "latest_timestamp": timestamp,
                        "City": city,
                        "Area": area,
                        "Paid": False,
                        "Count": 1,
                    })
                    response['success'] = True
                except:
                    response['success'] = False
                    response['error'] = "No such user present"

        except pymongo.errors.OperationFailure as e:
            print(e)
            response['success'] = False
            response['error'] = "Couldn't connect to Mongo DB"
    else:
        # Enter data in 'Speed' collection
        try:
            database.speed.insert(
                {"vehicle_no": vehicle_no, "lat": lat, "lng": lng, "speed": speed, "timestamp": timestamp,
                 "road": road, "direction": direction})
            response['success'] = True
        except pymongo.errors.OperationFailure as e:
            print(e)
            response['success'] = False

    return JsonResponse(response, safe=False)


@csrf_exempt
def get_speed(request):
    lat = request.POST['lat']
    lng = request.POST['lng']
    response = {}
    try:
        speeds = database.speed.find({"lat": lat, "lng": lng})
        speed_data = []
        for speed in speeds:
            speed_data.append(speed.get("speed"))
        response['speed_data'] = speed_data
        response['success'] = True

    except pymongo.errors.OperationFailure:
        response['success'] = False

    return JsonResponse(response, safe=False)


def get_speed_limit(lat, lng, road, direction,speed_by_vr,distance):
    nearby_speed = nearbyvehicles.get_nearby_vehicles_speed(
        lat, lng, road, 0)
    nearby_speed = median(nearby_speed.values())

    if distance < 100:
        return min(speed_by_vr,20)
    else:
        return (speed_by_vr + nearby_speed)//2

@csrf_exempt
def get_vehicle_list(request):
    lat = float(request.POST['lat'])
    lng = float(request.POST['lng'])
    response = {}
    road = 'Unknown'
    direction = 0
    vehicle_list = nearbyvehicles.get_nearby_vehicles_speed(
        lat, lng, road, direction)
    response['vehicle_list'] = vehicle_list
    return JsonResponse(response, safe = False)



@csrf_exempt
def get_speed_recommend(request):
    lat = float(request.POST['lat'])
    lng = float(request.POST['lng'])
    response = {}
    road = 'Unknown'
    direction = 0
    vehicle_list = nearbyvehicles.get_nearby_vehicles_speed(
        lat, lng, road, direction)
    response['limit'] = median(vehicle_list)
    return JsonResponse(response, safe= False)