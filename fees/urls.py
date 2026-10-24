from django.urls import path
from . import views

urlpatterns = [
    path('summary/', views.fee_summary_view, name='fee_summary'),
]
