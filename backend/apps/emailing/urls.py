from django.urls import path
from .views import AlertEmailingView, SendAlertEmailView

urlpatterns = [
    path('emailing/<uuid:alert_id>/', AlertEmailingView.as_view(), name='alert-emailing'),
    path('alerts/<uuid:alert_id>/send-email/', SendAlertEmailView.as_view(), name='alert-send-email')
]