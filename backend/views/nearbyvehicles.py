from . import nearby_area
import os
import pymongo
import math
from statistics import mean, median

client = pymongo.MongoClient(os.environ["SPEEDCOP_DATABASE"])
database = client.sihdatabase


def get_nearby_vehicles_speed(lat, lng, road, direction):
    lat1, lng1 = nearby_area.get_latlng(lat, lng, 200, 200)
    lat2, lng2 = nearby_area.get_latlng(lat, lng, -200, -200)

    if lat2 > lat1:
        lat1, lat2 = lat2, lat1
    if lng2 > lng1:
        lng1, lng2 = lng2, lng1

    # if road == "Unknown":
    #     query = {'$and': [{'lat': {'$lt': lat1, '$gt': lat2}}, {'lng': {'$lt': lng1, '$gt': lng2}},
    #                       {'direction': {'$lt': direction + 45, '$gt': direction - 45}}]}
    # else:
    #     query = {'$and': [{'lat': {'$lt': lat1, '$gt': lat2}}, {'lng': {'$lt': lng1, '$gt': lng2}}, {'road': road},
    #                       {'direction': {'$lt': direction + 45, '$gt': direction - 45}}]}
    if road == "Unknown":
        query = {'$and': [{'lat': {'$lt': lat1, '$gt': lat2}}, {'lng': {'$lt': lng1, '$gt': lng2}},{'direction': 0}]}
    else:
        query = {'$and': [{'lat': {'$lt': lat1, '$gt': lat2}}, {'lng': {'$lt': lng1, '$gt': lng2}}, {'road': road},
                    {'direction': {'$lt': direction + 45, '$gt': direction - 45}}]}
    vehicles = ""
    try:
        vehicles = database.speed.find(query)
        # database.speed.find({"$and": [{"lat": {"$gt": 18.47226068471588, "$lt": 18.474057315284117}},
        #                               {"lng": {"$lt": 73.88170111820448, "$gt": 73.87980688179552}}]})
        # print("--------------------------------------------------------------------------")
        # for vehicle in vehicles:
        #     print(vehicle)
        # print("--------------------------------------------------------------------------")
    except pymongo.errors.OperationFailure as e:
        print(e)
    response = {}
    vehicle_list = []
    vehicle_name = []
    print(vehicles)
    for vehicle in vehicles:
        response[vehicle['vehicle_no']] = vehicle['speed']
    
    length = len(response.values())

    if len(response.values()) < 5:
        # If there are less vehicles in the vicinity then ignore speed
        return 0
    else:

        return response


def get_vehicle_direction(lat1, lng1, lat2, lng2):
    radians = math.atan2((lat2 - lat1), (lng2 - lng1))
    degree = radians * (180 / math.pi)
    return degree
