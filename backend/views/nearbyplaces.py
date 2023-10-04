from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

import json
import requests
from geopy.distance import geodesic

URL = "https://nominatim.openstreetmap.org/search.php?q=PLACE_TYPE+near+[LOCATION]&format=json&limit=15"



def get_nearby_places(lat,lng):

    location = [lat, lng]
    url = URL.replace('LOCATION', lat + ',' + lng)
    url = url.replace('PLACE_TYPE', 'school')
    print(url)
    schools_list = requests.get(url)
    schools_list = json.loads(schools_list.text)

    url = URL.replace('LOCATION', lat + ',' + lng)
    url = url.replace('PLACE_TYPE', 'hospital')
    print(url)
    hospitals_list = requests.get(url)
    hospitals_list = json.loads(hospitals_list.text)

    schools = []
    hospitals = []
    
    s = []
    for school in schools_list:
        name = school['display_name']
        new_lat = float(school['lat'])
        new_lng = float(school['lon'])

        distance = int(geodesic((new_lat, new_lng), (lat, lng)).m)
        # s.append({'latlng': str(new_lat) + "," + str(new_lng), 'distance': distance})

        # Only get the schools in 1KM area
        if distance < 1000:
            schools.append({'name':name,'lat': lat, 'lng': lng, 'distance': distance})

    # print(s)
    for hospital in hospitals_list:
        name = hospital['display_name']
        new_lat = float(hospital['lat'])
        new_lng = float(hospital['lon'])

        distance = int(geodesic((new_lat, new_lng), (lat, lng)).m)
        
        # Only get the hospitals in 1KM area
        if distance < 1000:
            hospitals.append({'name':name,'lat': lat, 'lng': lng, 'distance': distance})
    # print(schools_list)
    # print(hospitals_list)
    response = {"schools": schools, "hospitals": hospitals, "location": location}

    return response
