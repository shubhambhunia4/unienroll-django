from django.urls import path
from . import views

urlpatterns = [
    path('courses/', views.course_catalog_view, name='course_catalog'),
    path('toggle/<int:course_id>/', views.toggle_course_enrollment, name='toggle_course'),
    path('my-courses/', views.my_courses_view, name='my_courses'),
    path('transcript/', views.academic_transcript_view, name='academic_transcript'),
    path('transcript/<int:student_id>/', views.academic_transcript_view, name='academic_transcript_admin'),
    path('admin-manage/', views.admin_enrollment_manage_view, name='admin_enrollment_manage'),
    path('admin-unlock/<int:enrollment_id>/', views.admin_unlock_enrollment, name='admin_unlock_enrollment'),
]
