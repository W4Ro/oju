from django.urls import path
from .views import ConfigurationViewSet


urlpatterns = [
    path('', ConfigurationViewSet.as_view({
        'get': 'list',
        'put': 'update'
    }), name='configuration'),
    path('toggle-proxy/',
         ConfigurationViewSet.as_view({
             'post': 'toggle_proxy'
         }), name="proxy-active-toggle"),
    path('toggle-host/',
         ConfigurationViewSet.as_view({
             'post': 'toggle_host'
         }), name='toggle-host-active'),
    path('toggle-alert/',
         ConfigurationViewSet.as_view({
             'post': 'toggle_alert'
         }), name="toggle-host-alert")
]