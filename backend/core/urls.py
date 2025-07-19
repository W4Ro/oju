
from django.contrib import admin
from django.urls import path, include, re_path
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from django.conf import settings

schema_view = get_schema_view(
    openapi.Info(
        title="Oju API",
        default_version='v1',
        description="API documentation for Oju",
        contact=openapi.Contact(email=settings.SUPPORT_EMAIL),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
    
)

urlpatterns = [
    re_path(r'^swagger/$', schema_view.with_ui('swagger', cache_timeout=0), name="schema-swagger-ui"),
    path('admin/', admin.site.urls),
    path('api/users/', include('apps.users.urls')),
    path('api/emailing/', include('apps.emailing.urls')),
    path('api/integrations/', include('apps.tools_integrated.urls')),
    path('api/config/', include('apps.config.urls')),
    path('api/roles/', include('apps.roles.urls')),
    path('api/mail-settings/', include('apps.mail_setting.urls')),
    path('api/alerts/', include('apps.alertes.urls')),
    path('api/defacements/', include('apps.defacement.urls')),
    path('api/vendor-list/', include('apps.AV_vendor.urls')),
    path('api/logs/', include('apps.logsFonc.urls')),
    path('api/focal-points/', include('apps.focal_points.urls')),
    path('api/entities/', include('apps.entities.urls')),
    path('api/cerb_scans/', include('apps.cerb_scans.urls')),
    path('api/dashboard/', include('apps.dashboard.urls')),
]
