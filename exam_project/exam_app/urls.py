from django.urls import path
from . import views

urlpatterns = [
    path('', views.vkexam_list, name='home'),  # Главная страница
    path('vkexam/', views.vkexam_list, name='vkexam_list'),
]
