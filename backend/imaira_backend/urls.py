"""
IMAIRA+ URL Configuration
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from api import views

urlpatterns = [
    # Root & Health Check for Headless/Decoupled Backend Access
    path('', views.root_view, name='root'),
    path('health', views.health_check, name='health_no_slash'),
    path('health/', views.health_check, name='health'),
    
    # Django Admin
    path('admin/', admin.site.urls),
    
    # REST API Endpoints
    path('api/', include('api.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
