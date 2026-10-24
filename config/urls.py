"""
URL configuration for UniEnroll project.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from .views import HomeView
from . import api_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', HomeView.as_view(), name='home'),
    path('accounts/', include('accounts.urls')),
    path('academics/', include('academics.urls')),
    path('enrollment/', include('enrollment.urls')),
    path('fees/', include('fees.urls')),
    path('payments/', include('payments.urls')),

    # REST API Endpoints (Phase 6, 8 & 9)
    path('api/v1/health/', api_views.api_system_health, name='api_system_health'),
    path('api/v1/courses/', api_views.api_courses_list, name='api_courses_list'),
    path('api/v1/student/transcript/', api_views.api_student_transcript, name='api_student_transcript'),
    path('api/v1/admin/analytics/', api_views.api_admin_analytics, name='api_admin_analytics'),
    path('api/v1/admin/audit-logs/', api_views.api_admin_audit_logs, name='api_admin_audit_logs'),
    path('api/v1/ai-advisor/', api_views.api_ai_advisor, name='api_ai_advisor'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
