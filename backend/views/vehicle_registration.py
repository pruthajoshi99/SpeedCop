import os
import pymongo
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render

client = pymongo.MongoClient(os.environ["SPEEDCOP_DATABASE"])

database = client.sihdatabase


@csrf_exempt
def vehicle_registration(request, vehicle_id):
    if request.method == "GET":
        vehicle = database.vehicles.find({"vehicle_id": vehicle_id})
        vehicles = []
        for veh in vehicle:
            vehicles.append(veh)
        # if list is not empty means vehicle already registered
        print(vehicles)
        if len(vehicles) == 0:
            # Register the vehicle
            return render(request, "vehicle-registration.html", {"vehicle_id": vehicle_id})
        else:
            # Already Registered
            return render(request, "vehicle-registration.html",
                          {"vehicle": vehicles, "vehicle_id": vehicle_id})
    else:
        # Post data from the form
        name = request.POST['ownername']
        vehicle_no = request.POST['vehicle_no']
        email = request.POST['email']
        vehicles = [{'name': name, 'vehicle_no': vehicle_no, 'vehicle_id': vehicle_id, 'email': email}]
        print(name, vehicle_no, vehicle_id, email)
        try:
            database.vehicles.insert(vehicles[0])
            messages = "Vehicle Added Successfully"
            return render(request, "vehicle-registration.html",
                          {"vehicle": vehicles, "vehicle_id": vehicle_id, "messages": messages})
        except pymongo.errors.OperationFailure as e:
            messages = e
            return render(request, "vehicle-registration.html",
                          {"errors": messages, "vehicle_id": vehicle_id})
