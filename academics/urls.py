from django.urls import path
from . import views

urlpatterns = [
    path('admin/courses/', views.admin_course_list_view, name='admin_course_list'),
    path('admin/courses/create/', views.admin_course_create_view, name='admin_course_create'),
    path('admin/courses/<int:course_id>/edit/', views.admin_course_edit_view, name='admin_course_edit'),
    path('admin/courses/<int:course_id>/delete/', views.admin_course_delete_view, name='admin_course_delete'),
    path('announcements/', views.announcements_list_view, name='announcements_list'),
    path('admin/announcements/create/', views.announcement_create_view, name='announcement_create'),
    path('admin/grades/', views.admin_grade_roster_view, name='admin_grade_roster'),
    path('admin/grades/<int:item_id>/assign/', views.assign_grade_view, name='assign_grade'),
]
