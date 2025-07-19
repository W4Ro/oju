from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import AVVendorViewSet

router = DefaultRouter()
router.register(r'', AVVendorViewSet)

urlpatterns = [
    path('', include(router.urls)),
]