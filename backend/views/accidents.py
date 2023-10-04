from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

import os
import pymongo
from datetime import datetime
import pytz
import random
from . import reverse_geocoding


client = pymongo.MongoClient(os.environ["SPEEDCOP_DATABASE"])

database = client.sihdatabase

@csrf_exempt
def report_accident(request):
    lat = request.POST['lat']
    lng = request.POST['lng']
    vehicle_no = request.POST['vehicle_no']
    timestamp = datetime.now(pytz.timezone('Asia/Kolkata'))
    speed = request.POST['speed']
    response = {}
    address = reverse_geocoding.get_location(lat,lng)
    try:
        database.accidents.insert({"vehicle_no": vehicle_no,"lat": lat, "lng": lng, "speed": speed, "timestamp": timestamp, "Area" : address['features'][0]['properties']['address']['county'], "City" : address['features'][0]['properties']['address']['state_district']})
        response["success"] = 1
        
    except  pymongo.errors.OperationFailure:
        response["success"] = 0

    return JsonResponse(response,safe = False)

            
    
@csrf_exempt
def count_accident(request):
    lat = request.POST['lat']
    lng = request.POST['lng']
    response = {}  
    try:
        number_of_accidents = (database.accidents.find({"lat": lat, "lng": lng}).count())
        response["number_of_accidents"] = number_of_accidents
        response["success"] = 1

    except  pymongo.errors.OperationFailure:
        response["success"] = 0
    
    return JsonResponse(response,safe = False)

def count_accident():
    # lat = request.POST['lat']
    # lng = request.POST['lng']
    # response = {}
    # try:
    acc_list = [True, False, False, False, False]
    index = random.randint(0, 4)
    # number_of_accidents = (database.accidents.find({"lat": lat, "lng": lng}).count())
    # response["number_of_accidents"] = number_of_accidents
    # response["success"] = 1
    return acc_list[index]
    # except pymongo.errors.OperationFailure:
    #     response["success"] = 0

    # return JsonResponse(response, safe=False)