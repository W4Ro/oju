from rest_framework import viewsets, status
from django.contrib.auth import authenticate
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken, TokenError
from django.core.cache import cache
from datetime import timedelta
from django.utils import timezone
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from .serializers import (
    UserCreateSerializer, UserSerializer, ChangePasswordSerializer,
    UserProfileUpdateSerializer,UserRegisterSerializer, UserUpdateSerializer,
    ResetPasswordSerializer, UserProfileSerializer)
from core.common_function import str_exception
from rest_framework.exceptions import ValidationError
from django.core.validators import validate_email
from .models import User,PasswordReset, BlacklistedToken
from apps.roles.models import Role, RolePermission
from apps.roles.permissions import HasPermission
from apps.logsFonc.utils import create_system_log
from core.common_function import *
import uuid
from django.template.loader import render_to_string
from django.contrib.auth.password_validation import validate_password
from apps.mail_setting.tasks import send_email_task
from core.definitions import *
from django.conf import settings
from django.db import transaction

import logging
logger = logging.getLogger(__name__)

class AuthViewSet(viewsets.GenericViewSet):
    permission_classes = []
    serializer_class = UserRegisterSerializer
    http_method_names = ['post']
    
    def get_role_permissions(self, role_id):
        """Retrieves the list of permissions for a given role"""
        try:
            if not Role.objects.filter(
                id=role_id,
                is_active=True
            ).exists():
                return []
            return list(RolePermission.objects.filter(
                role_id=role_id
            ).values_list('permission__permission_code', flat=True))
        except:
            return []
    
    @swagger_auto_schema(
        operation_summary="New User Registration",
        operation_description="Allows a user to register on the platform. The account created will be inactive by default.",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['email', 'username', 'nom_prenom', 'password', 'confirm_password'],
            properties={
                'email': openapi.Schema(type=openapi.TYPE_STRING),
                'username': openapi.Schema(type=openapi.TYPE_STRING),
                'nom_prenom': openapi.Schema(type=openapi.TYPE_STRING),
                'password': openapi.Schema(type=openapi.TYPE_STRING),
                'confirm_password': openapi.Schema(type=openapi.TYPE_STRING)
            }
        ),
        responses={
            201: openapi.Response(
                description="Success",
                examples={
                    "application/json": {
                        "status": "success"
                    }
                }
            ),
            400: "Bad request - Missing required fields"
        },
        tags=['Authentication']
    )
    @action(detail=False, methods=['post'])
    def register(self, request):
        """Register a new user"""
        try:
            error, data = assignment_check({'email', 'username', 'nom_prenom', 'password', 'confirm_password'}, request.data.items())
            if error:
                return Response(
                    {"error": data},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            serializer = self.get_serializer(data=data)
            serializer.is_valid(raise_exception=True)
            user = serializer.save()
            
            return Response(
                {"success": "Your account has been created, please contact admin to enable it"},
                status=status.HTTP_201_CREATED
            )
        except ValidationError as e:
            return Response(
                {"error": str_exception(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            return Response(
                {"error": "An error occured processing your request"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


    @swagger_auto_schema(
        operation_summary="User login",
        operation_description="Authenticates a user and returns access tokens",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['email', 'password'],
            properties={
                'email': openapi.Schema(type=openapi.TYPE_STRING, description="User Email"),
                'password': openapi.Schema(type=openapi.TYPE_STRING, description="Password")
            }
        ),
        responses={
            200: openapi.Response(
                description="Authentication successful",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'access': openapi.Schema(type=openapi.TYPE_STRING, description="Access token"),
                        'user': openapi.Schema(type=openapi.TYPE_STRING, description="Refresh token"),
                        'permissions': openapi.Schema(type=openapi.TYPE_STRING, description="A list of user permissions"),
                    }
                )
            ),
            401: "Invalid credentials",
            403: "Account disabled",
            429: "Too many login attempts"
        },
        tags=['Authentication']
    )
    @action(detail=False, methods=['post'])
    def login(self, request):
        """user login"""
        try:
            error, data = assignment_check({'email', 'password'}, request.data.items())
            if error:
                return Response(
                    {"error": data},
                    status=status.HTTP_400_BAD_REQUEST
                )
            email = data.get('email', '').strip()
            password = data.get('password', '')
            
            with transaction.atomic():
                user = User.objects.select_for_update().filter(email=email).first()
                
                
                lockout_time = LOGIN_LOCKOUT_TIME 
                max_attempts = LOGIN_MAX_ATTEMPTS
                
                if user and user.failed_login_attempts >= max_attempts:
                    
                    if user.last_failed_login and (timezone.now() - user.last_failed_login).seconds < lockout_time:
                        remaining_time = lockout_time - (timezone.now() - user.last_failed_login).seconds
                        
                        return Response(
                            {
                                'error': f'Too many login attempts. Try again in {int(remaining_time)} secondes.'
                            },
                            status=status.HTTP_429_TOO_MANY_REQUESTS
                        )
                    else:
                        user.failed_login_attempts = 0
                        user.save()
                
                user_auth = authenticate(email=email, password=password)

                if not user_auth:
                    if user:
                        create_system_log(assign_user(data.get('email', '')), 'Authentication failed')
                        user.failed_login_attempts +=1
                        user.last_failed_login = timezone.now()
                        user.save()
                    return Response(
                        {'error': 'incorrect username or password'},
                        status=status.HTTP_401_UNAUTHORIZED
                    )
                if not user_auth.is_active:
                    create_system_log(assign_user(data.get('email', '')), 'Disable account connexion attempted')
                    return Response(
                        {'error': 'This account is disabled'},
                        status=status.HTTP_403_FORBIDDEN
                    )
                user_auth.failed_login_attempts = 0
                user_auth.last_login = timezone.now()
                user_auth.save()

                refresh = RefreshToken.for_user(user_auth)
                refresh['role_id'] = str(user_auth.role_id)
                permissions = self.get_role_permissions(user_auth.role_id)

                access_token = refresh.access_token
                token_iat = access_token.payload.get('iat')

                blacklist_time = timezone.datetime.fromtimestamp(
                    token_iat - 10, 
                    tz=timezone.get_current_timezone()
                )  # 10 seconds before the token was issued

                BlacklistedToken.objects.update_or_create(
                    token='ALL',
                    user=user_auth,
                    defaults={
                        'blacklisted_at': blacklist_time,
                        'reason': 'New login - all previous sessions terminated'
                    }
                )
                create_system_log(assign_user(data.get("email", '')), "User logged in (all previous sessions terminated)")
                
                

                return Response({
                    'access': str(refresh.access_token),
                    'refresh': str(refresh),
                    'permissions': permissions
                },
                status=status.HTTP_200_OK)
        except Exception as e:
            return Response(
                {"error": "An error occured processing your request"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @swagger_auto_schema(
        operation_summary="Logout",
        operation_description="Revokes the refresh token",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['email', 'password'],
            properties={
                'refresh': openapi.Schema(type=openapi.TYPE_STRING, description="User refresh token")
            }
        ),
        responses={
            200: "Logout successful",
            400: "Invalid Token"
        },
        tags=['Authentication']
    )
    @action(detail=False, methods=['post'], permission_classes=[IsAuthenticated])
    def logout(self, request):
        """User Logout"""
        try:
            refresh_token = request.data.get('refresh')
            if not refresh_token:
                return Response(
                    {'error': 'No active session'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            if not request.user.is_authenticated:
                return Response(
                    {'error': 'User is not authenticated'},
                    status=status.HTTP_401_UNAUTHORIZED
                )
            try:
                token = RefreshToken(refresh_token)
                
                if (token.get('user_id')) != str(request.user.id):
                    return Response(
                        {"error": "Token invalid for this user"},
                        status=status.HTTP_403_FORBIDDEN
                    )
                if BlacklistedToken.objects.filter(token=refresh_token).exists():
                    return Response(
                        {"error": 'Invalid token'},
                        status=status.HTTP_400_BAD_REQUEST
                    )
                access_token = request.headers.get('Authorization', '').split(' ')[1]
                if BlacklistedToken.objects.filter(
                    token__in=[refresh_token, access_token]
                ).exists():
                    create_system_log(assign_user(request.user), "User logout")
                    return Response(
                        {"error": 'Disconnected successfully'},
                        status=status.HTTP_200_OK
                    )
               
                BlacklistedToken.objects.bulk_create([
                    BlacklistedToken(token=refresh_token, user=request.user, reason='Logout'),
                    BlacklistedToken(token=access_token, user=request.user, reason='Logout')
                ])
                request.session.flush()
               
                return Response(
                    {'message': 'Logout successfull'},
                    status=status.HTTP_200_OK
                    )
            except TokenError:
                return Response(
                    {'error': "Invalid Token "},
                    status=status.HTTP_400_BAD_REQUEST
                )
        except Exception as e:
            return Response(
                {'error': "An error occured processing your request"},
                status=status.HTTP_400_BAD_REQUEST
            )
    @swagger_auto_schema(
        operation_summary="Refresh Access Token",
        operation_description="Use the refresh token to generate a new access token",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['refresh'],
            properties={
                'refresh': openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description="Refresh token"
                )
            }
        ),
        responses={
            200: openapi.Response(
                description="New tokens generated successfully",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'access': openapi.Schema(type=openapi.TYPE_STRING),
                        'refresh': openapi.Schema(type=openapi.TYPE_STRING)
                    }
                )
            ),
            401: "Invalid or expired token",
            400: "Missed token"
        },
        tags=['Authentication']
    )
    @action(detail=False, methods=['post'], permission_classes=[IsAuthenticated])
    def refresh_token(self, request):
        """Refresh user access token"""
        try:
            refresh_token = request.data.get('refresh')
            if not refresh_token:
                return Response(
                    {'error': 'Refresh token required'},
                    status=status.HTTP_400_BAD_REQUEST
                )
           
            if BlacklistedToken.objects.filter(token=refresh_token).exists():
                return Response(
                    {'error': 'Token revoqued'},
                    status=status.HTTP_401_UNAUTHORIZED
                )

            token = RefreshToken(refresh_token)
            user_id = token.get('user_id')

            with transaction.atomic():
                try:
                    user = User.objects.select_for_update().get(id=user_id)
                except User.DoesNotExist:
                    return Response(
                        {'error': 'User not found'},
                        status=status.HTTP_401_UNAUTHORIZED
                    )
                
                all_blacklist_entry = BlacklistedToken.objects.filter(
                    token='ALL',
                    user=user
                ).order_by('-blacklisted_at').first()
                
                if all_blacklist_entry:
                    iat_datetime = timezone.datetime.fromtimestamp(
                        token['iat'], 
                        tz=timezone.get_current_timezone()
                    )
                    if all_blacklist_entry.blacklisted_at > iat_datetime:
                        return Response(
                            {'error': 'Token blacklisted'},
                            status=status.HTTP_401_UNAUTHORIZED
                        )
                
                BlacklistedToken.objects.update_or_create(
                    token='ALL',
                    user=user,
                    defaults={
                        'blacklisted_at': timezone.now() - timedelta(seconds=2),
                        'reason': 'Token refresh - previous sessions terminated'
                    }
                )

                new_refresh = RefreshToken.for_user(user)
                new_refresh['role_id'] = str(user.role_id)
                
                return Response({
                    'access': str(new_refresh.access_token),
                    'refresh': str(new_refresh)
                })

        except TokenError:
            return Response(
                {'error': 'Token invalid or expired'},
                status=status.HTTP_401_UNAUTHORIZED
            )
        except Exception as e:
            return Response(
                {'error': "An error occured processing your request"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
class UserViewSet(viewsets.ModelViewSet):
    def get_permissions(self):
        """Get required permissions based on action"""
        permission_map = {
            'list': 'users_view',
            'retrieve': 'users_view',
            'create': 'users_create',
            'update': 'users_edit',
            'partial_update': 'users_edit',
            'destroy': 'users_delete',
            'toggle_active': 'users_toggle',
        }
        
        permission_code = permission_map.get(self.action)
        return [IsAuthenticated(), HasPermission(permission_code)] if permission_code else [IsAuthenticated()]
    queryset = User.objects.all()
    http_method_names = ['get', 'post', 'delete','put']
    
    def get_user_permissions(self, user):
        """Retrieve user permissions"""
        try:
            if not Role.objects.filter(
                id=user.role_id,
                is_active=True
            ).exists():
                return []
            return list(RolePermission.objects.filter(
                role_id=user.role_id
            ).values_list('permission__permission_code', flat=True))
        except Exception as e:
            return []

    def get_queryset(self):
        """Filter users by permissions"""
        user = self.request.user
        
        if self.action in ['me', 'change_password']:
            return User.objects.filter(id=user.id)
        
        if 'users_view' not in self.get_user_permissions(user):
            return User.objects.filter(id=user.id)
        return User.objects.all()
    
    def get_serializer_class(self):
        if self.action == 'create':
            return UserCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return UserUpdateSerializer
        elif self.action == 'me':
            return UserProfileSerializer
        return UserSerializer



    @swagger_auto_schema(
        operation_summary="List of users",
        operation_description="Retrieves the list of all users",
        responses={
            200: openapi.Response(
                description="List of users",
                schema=UserSerializer(many=True)
            )
        },
        tags=['Users']
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Create user",
        operation_description="Create new user",
        request_body=UserCreateSerializer,
        responses={
            201: UserSerializer,
            400: "Bad Requests",
            403: "Permission denied"
        },
        tags=['Users']
    )
    def create(self, request, *args, **kwargs):
        try:
            error, data = assignment_check({
                'email', 'username', 'nom_prenom', 
                'password', 'role', 'is_active', 'confirm_password'
            }, request.data.items())
            if error:
                return Response(
                    {"error": data},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            serializer = self.get_serializer(data=data)
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            create_system_log(assign_user(request.user), f"Create user: {data.get('email', '')}, {data.get('username', '')}")
            return Response(
                serializer.data,
                status=status.HTTP_201_CREATED
            )
        except ValidationError as e:
            return Response(
                {"error": str_exception(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            return Response(
                {"error": "An error occured processing your request"},
                status=status.HTTP_400_BAD_REQUEST
            )

    @swagger_auto_schema(
        operation_summary="user details",
        operation_description="Retrieves details of a specific user",
        responses={
            200: UserSerializer,
            403: "Permission denied",
            404: "User not found",
        },
        tags=['Users']
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Update user",
        operation_description="Edits a user's information",
        request_body=UserUpdateSerializer,
        responses={
            200: UserSerializer,
            400: "Bad request",
            403: "Permission denied",
            404: "User not found"
        },
        tags=['Users']
    )
    def update(self, request, *args, **kwargs):
        try:
            partial = kwargs.pop('partial', False)
            instance = self.get_object()
            if instance.is_staff or instance.is_superuser:
                return Response(
                    {"error": "You can not apply this change to this user"},
                    status=status.HTTP_403_FORBIDDEN
                )
            error, data = assignment_check({
                'username', 'nom_prenom', 'role', 'is_active', 'email', 'current_password'
            }, request.data.items())
            if error:
                return Response(
                    {"error": data},
                    status=status.HTTP_400_BAD_REQUEST
                )
            if request.user.id == instance.id:
                return Response(
                    {"error": "Can not update your profile by this way"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            if 'users_manage_roles' not in self.get_user_permissions(request.user):
                if data.get('role') != str(instance.role_id):
                    return Response(
                        {"error": "You can not change this user's role"},
                        status=status.HTTP_403_FORBIDDEN
                    )
                    
            serializer = self.get_serializer(
                instance, 
                data=data, 
                partial=partial
            )
            serializer.is_valid(raise_exception=True)
            self.perform_update(serializer)
            BlacklistedToken.objects.update_or_create(
                    token='ALL',
                    user=instance,
                    defaults={
                        'blacklisted_at': timezone.now(), 
                        'reason': 'User profile updated'
                        }
                )
            create_system_log(assign_user(request.user), f"change user's profile {instance.username}")
            
            
            return Response(
                serializer.data,
                status=status.HTTP_200_OK
            )
        except ValidationError as e:
            return Response(
                {"error": str_exception(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            return Response(
                {"error": "An error occured processing your request"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
    @swagger_auto_schema(
        operation_summary="Edit a user",
        operation_description="Edits a user's information",
        request_body=UserProfileUpdateSerializer,
        responses={
            200: UserSerializer,
            400: "Bad request",
            403: "Permission denied",
            404: "User not found"
        },
        tags=['Users']
    )
    @action(detail=False, methods=['put'])
    def update_profile(self, request):
        """Updating the logged in user profile"""
        try:
            instance = request.user
            error, data = assignment_check({'username', 'email', 'nom_prenom', 'current_password'}, request.data.items())
            
            if error:
                return Response(
                    {"error": data},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            current_password = data.pop('current_password')
            if not instance.check_password(current_password):
                return Response(
                    {"error": "Password incorrect"},
                    status=status.HTTP_400_BAD_REQUEST
                )
        

            serializer = UserProfileUpdateSerializer(
                instance,
                data=data,
            )


            serializer.is_valid(raise_exception=True)
            serializer.save()
            create_system_log(assign_user(request.user), "Update his profile")
            return Response(
                serializer.data,
                status=status.HTTP_200_OK
            )
        except ValidationError as e:
            return Response(
                {"error": str_exception(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            return Response(
                {"error": "An error occured processing your request"},
                status=status.HTTP_400_BAD_REQUEST
            )

    @swagger_auto_schema(
        operation_summary="Delete a user",
        operation_description="Delete a user",
        responses={
            204: "User deleted",
            404: "User not found"
        },
        tags=['Users']
    )
    def destroy(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            if instance.is_staff or instance.is_superuser:
                return Response(
                    {"error": "You can not apply this change to this user"},
                    status=status.HTTP_403_FORBIDDEN
                )
            if instance.id == request.user.id:
                return Response(
                    {"error": 'You can not delete your own account'},
                    status=status.HTTP_403_FORBIDDEN
                )
            create_system_log(assign_user(request.user), f"Delete {instance.username} user's account")
            return super().destroy(request, *args, **kwargs)
        except Exception as e:
            return Response(
                {"error": "An error occured processing your request"},
                status=status.HTTP_400_BAD_REQUEST
            )

    @swagger_auto_schema(
        operation_summary="Logged in user profile",
        operation_description="Retrieves the profile of the currently logged in user",
        responses={
            200: UserProfileSerializer
        },
        tags=['Users']
    )
    @action(detail=False, methods=['get'])
    def me(self, request):
        """Retrieves the profile of the currently logged in user"""
        try:
            serializer = self.get_serializer(request.user)
            
            return Response(serializer.data)
        except Exception as e:
            return Response(
                {"error": "An error occured processing your request"},
                status=status.HTTP_400_BAD_REQUEST
            )

    @swagger_auto_schema(
        operation_summary="Change password",
        operation_description="Allows the user to change their password",
        request_body=ChangePasswordSerializer,
        responses={
            200: "Password changed successfully",
            400: "Bad Request"
        },
        tags=['Users']
    )
    @action(detail=False, methods=['post'], permission_classes=[IsAuthenticated])
    def change_password(self, request):
        """Change the password of the logged in user"""
        try:
            error, data = assignment_check({'old_password', 'new_password', 'confirm_password'}, request.data.items())
            if error:
                return Response(
                    {"error": data},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            serializer = ChangePasswordSerializer(data=data)
            
            serializer.is_valid(raise_exception=True)
            user = request.user
            if not user.check_password(serializer.validated_data['old_password']):
                return Response(
                    {'error': 'Incorrect old password'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            user.set_password(serializer.validated_data['new_password'])
            user.save()
            
            BlacklistedToken.objects.update_or_create(
                token='ALL',
                user=user,
                defaults={
                    'blacklisted_at': timezone.now(), 
                    'reason': 'Password changed'
                    }
                
            )
            create_system_log(assign_user(request.user), "Change his password")

            templates = render_to_string('confirmReset.html', {
                    'support_email': settings.SUPPORT_EMAIL
                })
            send_email_task.delay(
                subject = "Password reset successfully",
                body = templates,
                to_recipients = [user.email] ,
                is_html = True
                
            )

            return Response(
                {'message': 'Password changed successfully'},
                status=status.HTTP_200_OK
                    )
        except ValidationError as e:
            return Response(
                {"error": str_exception(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            return Response(
                {"error": "An error occured processing your request"},
                status=status.HTTP_400_BAD_REQUEST
                )

    @swagger_auto_schema(
        operation_summary="Enable/Disable a user",
        operation_description="change a user's status",
        responses={
            200: openapi.Response(
                description="Status successfully changed",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'message': openapi.Schema(type=openapi.TYPE_STRING)
                    }
                )
            ),
            403: "Permission denied",
            404: "User not found"
        },
        tags=['Users']
    )
    @action(detail=True, methods=['get'])
    def toggle_active(self, request, pk=None):
        """Enable/Disable a user"""
        try:
            user = self.get_object()
            if user.id ==  request.user.id:
                return Response(
                    {"error": "You can not apply this change to your own account"},
                    status=status.HTTP_403_FORBIDDEN
                )
            if user.is_staff or user.is_superuser:
                return Response(
                    {"error": "You can not apply this change to this user"},
                    status=status.HTTP_403_FORBIDDEN
                )
            user.is_active = not user.is_active
            user.save()

            if not user.is_active:
                
                BlacklistedToken.objects.update_or_create(
                    token='ALL',
                    user=user,
                    defaults={
                        'blacklisted_at': timezone.now(), 
                        'reason': 'User desactivated'
                        }
                )
            create_system_log(assign_user(request.user), f"Toggle user {user.username} status")
            return Response({
                'success': f"{user.is_active}"},
                status=status.HTTP_200_OK
            )
        except Exception as e:
            return Response(
                {'error': "An error occured processing your request"},
                status=status.HTTP_404_NOT_FOUND
            )

class PasswordResetViewSet(viewsets.GenericViewSet):
    permission_classes = []
    serializer_class = ResetPasswordSerializer

    # def get_throttles(self):
    #     """
    #     Rate limiting personnalisé pour les différentes actions
    #     """
    #     if self.action == 'request_reset':
    #         self.throttle_scope = 'password_reset_request'
    #     elif self.action == 'reset_password':
    #         self.throttle_scope = 'password_reset_confirm'
    #     return super().get_throttles()
    
    @swagger_auto_schema(
        operation_summary="Request a password reset",
        operation_description="Send an email with a password reset link",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['email'],
            properties={
                'email': openapi.Schema(type=openapi.TYPE_STRING)
            }
        ),
        responses={
            200: openapi.Response(
                description="Request processed successfully",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'message': openapi.Schema(type=openapi.TYPE_STRING)
                    }
                )
            ),
            429: "Trop de tentatives",
            400: 'Bad request'
        },
        tags=['Password Reset']
    )
    @action(detail=False, methods=['post'])
    def request_reset(self, request):
        """Request a password reset"""
        try:
            email = request.data.get('email', '').lower().strip()
            if not email:
                return Response(
                    {"error": "email field is required"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            validate_email(email)
            user = User.objects.filter(email=email, is_active=True).first()
            if user:
                with transaction.atomic():
                    user_locked = User.objects.select_for_update().filter(id=user.id).first()

                    recent_request = PasswordReset.objects.filter(
                        user=user_locked,
                        created_at__gte=timezone.now() - timedelta(minutes=15),
                        is_used=False
                    ).exists()
                    if recent_request:
                        return Response(
                            {"error": "A reset link was recently sent"},
                            status=status.HTTP_400_BAD_REQUEST
                        )
                    
                    PasswordReset.objects.filter(
                        user=user_locked,
                        is_used=False
                    ).delete()

                    token = str(uuid.uuid4())
                    PasswordReset.objects.create(
                        user=user_locked,
                        token=token,
                        expires_at = timezone.now() + timedelta(minutes=15)
                    )

                create_system_log(assign_user(user.email), "Request password reset")

                templates = render_to_string('passwordReset.html', {
                    'reset_link': f'{settings.FRONTEND_URL}/authentication/reset-password/{token}', 
                    'expiration_time': '15 minutes', 
                    'support_email': settings.SUPPORT_EMAIL
                })
                send_email_task.delay(
                    subject = "Password reset Request",
                    body = templates,
                    to_recipients = [email] ,
                    is_html = True
                    
                )
            return Response(
                {"success": 'If this email adresse has account, an reinitialisation email has been sent'},
                status=status.HTTP_200_OK
            )
            
        except Exception as e:
            return Response({
                'error': "An error occured processing your request"
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        

    @swagger_auto_schema(
        operation_summary="Reset Password",
        operation_description="Reset password with token received by email",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['token', 'password', 'confirm_password'],
            properties={
                'token': openapi.Schema(type=openapi.TYPE_STRING),
                'password': openapi.Schema(type=openapi.TYPE_STRING),
                'confirm_password': openapi.Schema(type=openapi.TYPE_STRING)
            }
        ),
        responses={
            200: openapi.Response(
                description="Password reset successfully",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'message': openapi.Schema(type=openapi.TYPE_STRING)
                    }
                )
            ),
            400: openapi.Response(
                description="Validation error",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'error': openapi.Schema(type=openapi.TYPE_STRING)
                    }
                )
            ),
            429: "Rate limit",
            400: "Bad Request"
        },
        tags=['Password Reset']
    )
    @action(detail=False, methods=['post'])
    def reset_password(self, request):
        """Reset password with token"""
        try:
            error, data = assignment_check({'token', 'password', 'confirm_password'}, request.data.items())
            if error:
                return Response(
                    {"error": data},
                    status=status.HTTP_400_BAD_REQUEST
                )
            serializer = self.get_serializer(data=data)
            serializer.is_valid(raise_exception=True)
            
            token = serializer.validated_data['token']
            password = serializer.validated_data['password']
            
            reset = PasswordReset.objects.filter(
                token=token,
                is_used=False,
                expires_at__gt=timezone.now()
            ).select_related('user').first()
            
            if not reset:
                return Response(
                    {'error': 'Invalid or expired token'},
                    status=status.HTTP_400_BAD_REQUEST
                )
                
            if reset.attempts >= 3:
                reset.is_used = True
                reset.save(update_fields=['is_used'])
                return Response(
                    {'error': 'Maximum number of attempts reached'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            reset.attempts += 1
            reset.save(update_fields=['attempts'])
            validate_password(password, reset.user)
            
            user = reset.user
            user.set_password(password)
            user.save()
            
            reset.is_used = True
            reset.save(update_fields=['is_used'])
            
            
            BlacklistedToken.objects.update_or_create(
                token='ALL',
                user=user,
                defaults={
                    'blacklisted_at': timezone.now(), 
                    'reason': 'Password Reset'
                    }
            )
            create_system_log(assign_user(user.email), f"Reinitialize his password")

            templates = render_to_string('confirmReset.html', {
                    'support_email': settings.SUPPORT_EMAIL
                })
            send_email_task.delay(
                subject = "Password reset successfully",
                body = templates,
                to_recipients = [user.email] ,
                is_html = True
                
            )
            
            return Response({
                'message': 'Password reset successfully. You can now log in.'
            })
        except ValidationError as e:
            return Response(
                {"error": str_exception(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            return Response(
                {"error": "An error occured processing your request"},
                status=status.HTTP_500_BAD_REQUEST
            )

    @swagger_auto_schema(
        operation_summary="Check the validity of a token",
        operation_description="Checks if a reset token is valid",
        manual_parameters=[
            openapi.Parameter(
                'token',
                openapi.IN_QUERY,
                description="Reset Token",
                type=openapi.TYPE_STRING,
                required=True
            )
        ],
        responses={
            200: openapi.Response(
                description="Statut du token",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'is_valid': openapi.Schema(type=openapi.TYPE_BOOLEAN),
                        'message': openapi.Schema(type=openapi.TYPE_STRING)
                    }
                )
            )
        },
        tags=['Password Reset']
    )
    @action(detail=False, methods=['get'])
    def verify_token(self, request):
        """Check the validity of a reset token"""
        try:
            token = request.query_params.get('token')
            
            if not token:
                return Response(
                    {
                        'is_valid': False,
                        'message': 'Token missed'
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            reset = PasswordReset.objects.filter(
                token=token,
                is_used=False,
                expires_at__gt=timezone.now()
            ).first()
            
            if not reset or reset.attempts >= 3:
                return Response({
                    'is_valid': False,
                    'message': 'Invalid token, expired or maximum number of attempts reached'
                })
            
            return Response({
                'is_valid': True,
                'message': 'Token valide'
            })
        except Exception as e:
            return Response(
                {"error": f"An error has occurred: {e}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )