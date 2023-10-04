from django.urls import path

from . import views

app_name = 'backend'

urlpatterns = [
    path('nearbyplaces', views.get_nearby_places, name='get_nearby_places'),
    path('accidents/reportaccident', views.report_accident, name='report_accident'),
    path('accidents/countaccident', views.count_accident, name='count_accident'),
    path('speed/getspeed', views.get_speed, name='get_speed'),
    path('speed/reportspeed', views.report_speed, name='report_speed'),
    path('vehicle_registration/<slug:vehicle_id>/', views.vehicle_registration, name='vehicle_registration'),
    path('vehicles/get-details', views.get_vehicle_details, name = 'get_vehicle_details')
]
