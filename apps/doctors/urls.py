from django.urls import path
from . import views

app_name = 'doctors'

urlpatterns = [
    path('', views.doctor_list, name='list'),
    path('search/', views.search_doctors, name='search'),
    path('<str:slug>/', views.doctor_detail, name='detail'),
    path('id/<int:doctor_id>/', views.doctor_detail_by_id, name='detail_by_id'),
]