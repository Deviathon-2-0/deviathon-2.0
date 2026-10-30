"""
IMAIRA+ URL Configuration
Merges top-level and namespaced /api routes for seamless decoupled access.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from api import views

urlpatterns = [
    # 1. Root & Health Check Endpoints
    path('', views.root_view, name='root'),
    path('health', views.health_check, name='health_no_slash'),
    path('health/', views.health_check, name='health'),
    
    # 2. Django Admin
    path('admin/', admin.site.urls),
    
    # 3. Namespaced REST API Endpoints (/api/...)
    path('api/', include('api.urls')),

    # 4. Direct Merged Top-Level Endpoints (/sessions/..., /tts/..., /roles/...)
    path('', include('api.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
