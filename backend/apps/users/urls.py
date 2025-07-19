from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import AuthViewSet, UserViewSet, PasswordResetViewSet

router = DefaultRouter()
router.register(r'', UserViewSet, basename='user')

urlpatterns = [
    # Routes for authentication
    path('auth/register/', AuthViewSet.as_view({'post': 'register'}), name='register'),
    path('auth/login/', AuthViewSet.as_view({'post': 'login'}), name='login'),
    path('auth/logout/', AuthViewSet.as_view({'post': 'logout'}), name='logout'),
    path('auth/refresh-token/', AuthViewSet.as_view({'post': 'refresh_token'}), name='refresh-token'),
    # route for password reset
    path('password/reset/request/', 
         PasswordResetViewSet.as_view({'post': 'request_reset'}),
         name='password-reset-request'),
    path('password/reset/verify/', 
         PasswordResetViewSet.as_view({'get': 'verify_token'}),
         name='password-reset-verify'),
    path('password/reset/', 
         PasswordResetViewSet.as_view({'post': 'reset_password'}),
         name='password-reset'),
     
    
    # include user routes
    path('', include(router.urls)),
]