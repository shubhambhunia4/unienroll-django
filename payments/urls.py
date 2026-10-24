from django.urls import path
from . import views

urlpatterns = [
    path('checkout/', views.initiate_checkout_view, name='checkout'),
    path('process-success/', views.process_payment_success, name='payment_success'),
    path('receipt/<str:transaction_id>/', views.payment_receipt_view, name='payment_receipt'),
    path('history/', views.payment_history_view, name='payment_history'),
    path('admin/analytics/', views.admin_analytics_dashboard_view, name='admin_analytics'),
    path('admin/financial-report/', views.admin_financial_report_view, name='admin_financial_report'),
    path('admin/export-csv/', views.export_financial_csv_view, name='export_financial_csv'),
    path('admin/mongodb-logs/', views.admin_mongodb_logs_view, name='admin_mongodb_logs'),
]
