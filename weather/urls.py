from django.urls import path
from .views import DashboardView
from .views import fetch_weather_data
urlpatterns = [
    path('', DashboardView.as_view(), name='dashboard'),
    path('fetch_weather/', fetch_weather_data, name='fetch_weather'),
     
]