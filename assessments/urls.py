from django.urls import path
from . import views

app_name = 'assessments'

urlpatterns = [
    path('', views.home, name='home'),
    path('association/<int:association_id>/', views.association_detail, name='association_detail'),
    path('assessment/<int:assessment_id>/', views.assessment_detail, name='assessment_detail'),
    path('unit-assessment/<int:unit_assessment_id>/', views.unit_assessment_detail, name='unit_assessment_detail'),
    path('assessment/<int:assessment_id>/pdf/', views.download_assessment_pdf, name='download_assessment_pdf'),
    path('assessment/<int:assessment_id>/report-2024/', views.payment_report_2024, name='payment_report_2024'),
    path('unit-assessment/<int:unit_assessment_id>/pdf/', views.download_unit_statement_pdf, name='download_unit_statement_pdf'),
    path('unit-assessment/<int:unit_assessment_id>/monthly-payments/', views.monthly_payments, name='monthly_payments'),
    path('unit-assessment/<int:unit_assessment_id>/adjust/', views.adjust_unit_assessment, name='adjust_unit_assessment'),
    path('unit-assessment/<int:unit_assessment_id>/payoff/', views.payoff_calculator, name='payoff_calculator'),
    path('unit-assessment/<int:unit_assessment_id>/edit-payoff/', views.edit_payoff, name='edit_payoff'),
]
