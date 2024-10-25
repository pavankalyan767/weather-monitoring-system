from django.contrib import admin
from .models import City, WeatherData, WeatherAlert, DailyWeatherSummary

@admin.register(City)
class CityAdmin(admin.ModelAdmin):
    list_display = ['name', 'latitude', 'longitude']
    search_fields = ['name']
    list_filter = ['name']

@admin.register(WeatherData)
class WeatherDataAdmin(admin.ModelAdmin):
    list_display = ['city', 'temperature', 'feels_like', 'condition', 'timestamp']
    list_filter = ['city', 'condition', 'timestamp']
    search_fields = ['city__name']
    date_hierarchy = 'timestamp'

@admin.register(WeatherAlert)
class WeatherAlertAdmin(admin.ModelAdmin):
    list_display = ['city', 'alert_type', 'message', 'timestamp']
    list_filter = ['city', 'alert_type', 'timestamp']
    search_fields = ['city__name', 'message']
    date_hierarchy = 'timestamp'

@admin.register(DailyWeatherSummary)
class DailyWeatherSummaryAdmin(admin.ModelAdmin):
    list_display = ['city', 'date', 'avg_temperature', 'max_temperature', 'min_temperature', 'dominant_condition']
    list_filter = ['city', 'date', 'dominant_condition']
    search_fields = ['city__name']
    date_hierarchy = 'date'