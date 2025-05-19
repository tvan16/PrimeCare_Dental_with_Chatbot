from django.urls import path
from . import views

urlpatterns = [
    path('services/', views.service_list, name='service_list'),
    path('<slug:slug>/', views.service_detail, name='service_detail'),
    path('subservice/<slug:slug>/', views.subservice_detail, name='subservice_detail'),
    path('dat-lich-bac-si/<slug:doctor_slug>/', views.book_doctor_appointment, name='book_doctor_appointment'),
]