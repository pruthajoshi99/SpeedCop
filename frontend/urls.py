"""User_Registration URL Configuration
The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name = 'home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name = 'home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
""" 

from os import name
from re import template
from django.urls import path,re_path
from django.contrib.auth import views as auth_views
from . import views
from rest_framework.authtoken import views as authviews
from .api import viewsets

app_name = 'frontend'

urlpatterns = [
    path('login', views.login_view, name = 'login'),
    path('dashboard', views.dashboard_view, name = 'dashboard'),
    path('accidents',views.accidents,name = 'accidents'),
    path('violations',views.violations,name = 'violations'),
    path('forgot-password', views.forgot_password_view, name = 'forgot password'),
    path('api/violations-data', viewsets.data_retrieval_api.as_view()),
    path('api/api-token-auth/', authviews.obtain_auth_token, name='api-token-auth'),
    path('api/accidents',viewsets.accidents_api.as_view()),
    path('api/violations',viewsets.violations_api.as_view()),
    path('forgot-password', auth_views.PasswordResetView.as_view(template_name = 'forgot-password.html', subject_template_name = 'forgot-password-subject.txt', email_template_name = 'forgot-password-email.html', success_url = 'forgot-password-done'), name = 'forgot-password'),
    path('forgot-password-done', auth_views.PasswordResetDoneView.as_view(template_name = 'forgot-password-email-notification.html'), name = 'forgot-password-done'),
    path('forgot-password-confirm/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name = 'forgot-password-screen.html',success_url = 'forgot-password-complete'), name = 'forgot-password-confirm'),
    path('forgot-password-confirm/<uidb64>/<token>/forgot-password-complete', auth_views.PasswordResetCompleteView.as_view(template_name = 'forgot-password-complete.html'), name = 'forgot-password-complete'),
    path('change-password', views.change_password_view, name = 'change-password'),
    path('api/violations-data', viewsets.data_retrieval_api.as_view(), name = 'api-violations-data'),
    path('api/api-token-auth/', authviews.obtain_auth_token, name = 'api-token-auth'),
    re_path(r'^api/city-by-state/$', views.CityList, name = 'city-by-state-detail'),
    path('api/change-password', viewsets.change_password_api.as_view(), name = 'api-change-password'),
    path('api/notify', viewsets.emailNotify.as_view(), name = 'email notify')

]
