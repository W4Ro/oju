from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import FocalFunctionViewSet, FocalPointViewSet

router = DefaultRouter()
router.register(r'function', FocalFunctionViewSet)
router.register(r'', FocalPointViewSet)

urlpatterns = [
    path('', include(router.urls)),
]