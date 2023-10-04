from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

import pymongo,os

client = pymongo.MongoClient(os.environ["SPEEDCOP_DATABASE"])

database = client.sihdatabase

@csrf_exempt
def get_vehicle_details(request):
    vehicle_id = request.POST['vehicle_id']
    response = dict()
    try:
        vehicle_details = database.vehicles.find_one({"vehicle_id" : vehicle_id})
        if vehicle_details:
            response["vehicle_details"] = {"vehicle_number" : vehicle_details['vehicle_no'], "owner_name" : vehicle_details['name']}
            response["success"] = True
        else: 
            response["success"] = False
            response["errors"] = "Module not registered"
    except  pymongo.errors.OperationFailure:
        response["success"] = False
        response["errors"] = "Cannot connect to Database"
    
    return JsonResponse(response,safe = False)
