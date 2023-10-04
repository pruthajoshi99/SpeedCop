from django.contrib.auth.models import User
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.mail import send_mail
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from rest_framework.response import Response
from rest_framework.generics import UpdateAPIView

from datetime import datetime, timedelta
import pymongo
import os

from .serializers import ChangePasswordSerializer
from speedcop.settings import EMAIL_HOST_USER


class data_retrieval_api(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        find_filter = {"City": request.user.location}
        client = pymongo.MongoClient(os.environ["SPEEDCOP_DATABASE"])
        database = client.sihdatabase
        data = []
        for x in database.violations.find(find_filter).sort('timestamp', pymongo.DESCENDING):
            value = {key: x[key] for key in x if key != '_id'}
            data.append(value)
        client.close()
        jsonresponse = {'username': request.user.username, 'violations': data}
        return JsonResponse(jsonresponse, safe=False)

    def post(self, request):
        filters = request.POST
        find_filter = dict()
        print(request.user.location)
        find_filter['$and'] = [{'City': request.user.location}]
        if 'violation_filter' in filters.keys():
            if filters['violation_filter'] == 'Recommended':
                find_filter['$and'].append({"$expr": {"$gt": ['$speed', '$recommendedspeed']}})
            else:
                find_filter['$and'].append({"$expr": {"$gt": ['$speed', '$speedlimit']}})
        if 'Above' in filters.keys():
            if filters['Above']:
                value = filters['Above']
                find_filter['$and'].append({'difference': {'$gt': value}})
        if 'Below' in filters.keys():
            if filters['Below']:
                value = filters['Below']
                find_filter['$and'].append({'difference': {'$lt': value}})
        if 'timestamp' in filters.keys():
            if filters['timestamp']:
                from_date = datetime.strptime(filters['timestamp'], '%Y-%m-%d')
                to_date = from_date + timedelta(days=1)
                find_filter['$and'].append({'timestamp': {'$gte': from_date, '$lte': to_date}})
        if 'state' in filters.keys():
            f = {'vehicle_no': {'$regex': '^' + filters['state']}}
            if 'rto' in filters.keys():
                f = {'vehicle_no': {'$regex': '^' + filters['state'] + filters['rto']}}
                if filters['code']:
                    f = {'vehicle_no': {'$regex': '^' + filters['state'] + filters['rto'] + filters['code']}}
                    if filters['number']:
                        f = {'vehicle_no': filters['state'] + filters['rto'] + filters['code'] + filters['number']}
            find_filter['$and'].append(f)
        if 'status_filter' in filters.keys():
            if filters['status_filter'] == 'Paid':
                find_filter['$and'].append({'Paid': True})
            elif filters['status_filter'] == 'Unpaid':
                find_filter['$and'].append({'Paid': False})
        client = pymongo.MongoClient(os.environ["SPEEDCOP_DATABASE"])
        database = client.sihdatabase
        data = []
        print(find_filter)
        for x in database.violations.find(find_filter).sort('timestamp', pymongo.DESCENDING):
            value = {key: x[key] for key in x if key != '_id'}
            data.append(value)
        client.close()
        jsonresponse = {'username': request.user.username, 'violations': data}
        return JsonResponse(jsonresponse, safe=False)


class change_password_api(UpdateAPIView):
    """
    An endpoint for changing password.
    """
    serializer_class = ChangePasswordSerializer
    model = User
    permission_classes = (IsAuthenticated,)

    def get_object(self, queryset=None):
        obj = self.request.user
        return obj

    def update(self, request, *args, **kwargs):
        self.object = self.get_object()
        serializer = self.get_serializer(data=request.data)

        if serializer.is_valid():
            # Check old password
            if not self.object.check_password(serializer.data.get("old_password")):
                return Response({"old_password": ["Wrong password."]}, status=status.HTTP_400_BAD_REQUEST)
            # set_password also hashes the password that the user will get
            self.object.set_password(serializer.data.get("new_password"))
            self.object.save()
            response = {
                'status': 'success',
                'code': status.HTTP_200_OK,
                'message': 'Password updated successfully',
                'data': []
            }

            return JsonResponse(response)
        return JsonResponse(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class accidents_api(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        n = 10
        find_filter = []
        heatmap_filter = dict()
        # find_filter.append({'$match':{'City': request.user.location}})
        filters = request.POST
        heatmap_filter['$and'] = [{'City': request.user.location}]

        print(filters)
        if 'time_filter' in filters:
            if filters['time_filter'] == 'months':
                n = 7
            elif filters['time_filter'] == 'years':
                n = 4
        if 'timestamp_from' in filters:
            if filters['timestamp_from'] != '':
                from_date = datetime.strptime(filters['timestamp_from'], '%Y-%m-%d')
                find_filter.append({'$match': {'timestamp': {'$gte': from_date}}})
                heatmap_filter['$and'].append({'timestamp': {'$gte': from_date}})

        if 'timestamp_till' in filters:
            if filters['timestamp_till'] != '':
                till_date = datetime.strptime(filters['timestamp_till'], '%Y-%m-%d')
                find_filter.append({'$match': {'timestamp': {'$lte': till_date}}})
                heatmap_filter['$and'].append({'timestamp': {'$lte': till_date}})

        if 'area' in filters:
            if filters['area'] != 'All':
                find_filter.append({'$match': {'Area': filters['area']}})
                heatmap_filter['$and'].append({'Area': filters['area']})
                find_filter.append({'$project': {'day': {'$substr': ["$timestamp", 0, n]}}})
                find_filter.append({'$group': {'_id': "$day", 'number': {'$sum': 1}}})
                find_filter.append({'$sort': {'_id': 1}})
            else:
                find_filter.append({'$match': {'Area': {'$ne': 'Unknown'}}})
                heatmap_filter['$and'].append({'Area': {'$ne': 'Unknown'}})

                find_filter.append({'$group': {'_id': "$Area", 'number': {'$sum': 1}}})
                find_filter.append({'$sort': {'_id': 1}})
        else:
            find_filter.append({'$match': {'Area': {'$ne': 'Unknown'}}})
            heatmap_filter['$and'].append({'Area': {'$ne': 'Unknown'}})
            find_filter.append({'$group': {'_id': "$Area", 'number': {'$sum': 1}}})
            find_filter.append({'$sort': {'_id': 1}})

        client = pymongo.MongoClient(os.environ["SPEEDCOP_DATABASE"])
        database = client.sihdatabase
        data = []
        areas = []
        latlngs = []
        for x in database.accidents.find(heatmap_filter):
            value = {key: x[key] for key in x if key in ['lat', 'lng']}
            latlngs.append(value)
        areas = database.accidents.find({'Area': {'$ne': 'Unknown'}}).distinct('Area')
        for x in database.accidents.aggregate(find_filter):
            data.append(x)
        client.close()
        jsonresponse = {'username': request.user.username, 'accidents': data, 'areas': areas, 'latlngs': latlngs}
        return JsonResponse(jsonresponse, safe=False)


class violations_api(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        heatmap_filter = dict()
        heatmap_filter['$and'] = [{'City': request.user.location}]

        n = 10
        find_filter = []
        # find_filter.append({'$match':{'City': request.user.location}})
        filters = request.POST
        if 'time_filter' in filters:
            if filters['time_filter'] == 'months':
                n = 7
            elif filters['time_filter'] == 'years':
                n = 4
        if 'timestamp_from' in filters:
            if filters['timestamp_from'] != '':
                from_date = datetime.strptime(filters['timestamp_from'], '%Y-%m-%d')
                find_filter.append({'$match': {'timestamp': {'$gte': from_date}}})
                heatmap_filter['$and'].append({'timestamp': {'$gte': from_date}})

        if 'timestamp_till' in filters:
            if filters['timestamp_till'] != '':
                till_date = datetime.strptime(filters['timestamp_till'], '%Y-%m-%d')
                find_filter.append({'$match': {'timestamp': {'$lte': till_date}}})
                heatmap_filter['$and'].append({'timestamp': {'$lte': till_date}})

        if 'area' in filters:
            if filters['area'] != 'All':
                heatmap_filter['$and'].append({'Area': filters['area']})
                find_filter.append({'$match': {'Area': filters['area']}})
                find_filter.append({'$project': {'day': {'$substr': ["$timestamp", 0, n]}}})
                find_filter.append({'$group': {'_id': "$day", 'number': {'$sum': 1}}})
                find_filter.append({'$sort': {'_id': 1}})
            else:
                heatmap_filter['$and'].append({'Area': {'$ne': 'Unknown'}})
                find_filter.append({'$match': {'Area': {'$ne': 'Unknown'}}})
                find_filter.append({'$group': {'_id': "$Area", 'number': {'$sum': 1}}})
                find_filter.append({'$sort': {'_id': 1}})

        else:
            heatmap_filter['$and'].append({'Area': {'$ne': 'Unknown'}})
            find_filter.append({'$match': {'Area': {'$ne': 'Unknown'}}})
            find_filter.append({'$group': {'_id': "$Area", 'number': {'$sum': 1}}})
            find_filter.append({'$sort': {'_id': 1}})

        client = pymongo.MongoClient(os.environ["SPEEDCOP_DATABASE"])
        database = client.sihdatabase
        data = []
        areas = []
        latlngs = []
        for x in database.violations.find(heatmap_filter):
            value = {key: x[key] for key in x if key in ['lat', 'lng']}
            latlngs.append(value)
        areas = database.violations.find({'Area': {'$ne': 'Unknown'}}).distinct('Area')
        for x in database.violations.aggregate(find_filter):
            data.append(x)
        client.close()
        print(latlngs)
        jsonresponse = {'username': request.user.username, 'violations': data, 'areas': areas, 'latlngs': latlngs}
        return JsonResponse(jsonresponse, safe=False)


class emailNotify(APIView):
    permissions_classes = (IsAuthenticated,)

    @csrf_exempt
    def post(self, request):
        email = request.POST['email']
        email_subject = "Reminder for payments due for your violation."
        email_messsage = "You receiving this email because you haven't paid your penalty for the violation of rules setup by SpeedCop."
        try:
            send_mail(email_subject, email_messsage, EMAIL_HOST_USER, [email, ], fail_silently=False)
            return JsonResponse({'success': True}, safe=False)
        except:
            return JsonResponse({'success': False}, safe=False)