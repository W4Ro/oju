from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import DefacementViewSet

router = DefaultRouter()
router.register(r'', DefacementViewSet)

urlpatterns = [
    path('', include(router.urls)),
]