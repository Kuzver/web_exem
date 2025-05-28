from django.urls import path
from . import views

urlpatterns = [
    path('', views.ipexam_list, name='home'),  # Главная страница
    path('ipexam/', views.ipexam_list, name='ipexam_list'),
]
