from django.urls import path, include
from .views import MailConfigViewSet
from rest_framework.routers import DefaultRouter, SimpleRouter

urlpatterns = [
    path('', MailConfigViewSet.as_view({
        'get': 'list',
        'put': 'update'
    }), name='mail-settings'),
    path('toggle_active/', 
         MailConfigViewSet.as_view({
             'post': 'toggle_status'
        }),
         name='mail-active-toggle'),
]