from django.contrib import admin
from django.utils.html import format_html
from django.db.models import Avg
from .models import City, WeatherData, DailyWeatherSummary



@admin.register(City)
class CityAdmin(admin.ModelAdmin):
    list_display = ['name', 'latitude', 'longitude', 'current_temperature', 'today_summary']
    search_fields = ['name']
    list_filter = ['name']
    
    def current_temperature(self, obj):
        latest_weather = WeatherData.objects.filter(city=obj).order_by('-timestamp').first()
        if latest_weather:
            return format_html(
                '<span style="color: {};">{:.1f}°C</span>',
                '#dc3545' if latest_weather.temperature > 30 else '#28a745',
                latest_weather.temperature
            )
        return '-'
    current_temperature.short_description = 'Current Temp'

    def today_summary(self, obj):
        summary = DailyWeatherSummary.objects.filter(city=obj).order_by('-date').first()
        if summary:
            return format_html(
                'Min: {:.1f}°C | Avg: {:.1f}°C | Max: {:.1f}°C',
                summary.min_temperature,
                summary.avg_temperature,
                summary.max_temperature
            )
        return '-'
    today_summary.short_description = 'Today\'s Summary'

@admin.register(WeatherData)
class WeatherDataAdmin(admin.ModelAdmin):
    list_display = [
        'city',
        'formatted_temperature',
        'formatted_feels_like',
        'condition',
        'humidity',
        'wind_speed',
        'timestamp'
    ]
    list_filter = ['city', 'condition', 'timestamp']
    search_fields = ['city__name', 'condition']
    date_hierarchy = 'timestamp'
    readonly_fields = ['timestamp']
    list_per_page = 50
    
    def formatted_temperature(self, obj):
        return format_html(
            '<span style="color: {};">{:.1f}°C</span>',
            '#dc3545' if obj.temperature > 30 else '#28a745',
            obj.temperature
        )
    formatted_temperature.short_description = 'Temperature'
    
    def formatted_feels_like(self, obj):
        return f'{obj.feels_like:.1f}°C'
    formatted_feels_like.short_description = 'Feels Like'
    
    fieldsets = (
        ('Location', {
            'fields': ('city',)
        }),
        ('Weather Data', {
            'fields': (
                'temperature',
                'feels_like',
                'condition',
                'humidity',
                'wind_speed'
            )
        }),
        ('Timestamp', {
            'fields': ('timestamp',)
        }),
    )

@admin.register(DailyWeatherSummary)
class DailyWeatherSummaryAdmin(admin.ModelAdmin):
    list_display = [
        'city',
        'date',
        'formatted_temperatures',
        'dominant_condition',
        'sample_count'
    ]
    list_filter = ['city', 'date', 'dominant_condition']
    search_fields = ['city__name']
    date_hierarchy = 'date'
    readonly_fields = ['condition_distribution_display']
    list_per_page = 30
    
    def formatted_temperatures(self, obj):
        return format_html(
            'Min: <span style="color: #28a745;">{:.1f}°C</span> | '
            'Avg: <span style="color: #007bff;">{:.1f}°C</span> | '
            'Max: <span style="color: #dc3545;">{:.1f}°C</span>',
            obj.min_temperature,
            obj.avg_temperature,
            obj.max_temperature
        )
    formatted_temperatures.short_description = 'Temperature Range'
    
    def condition_distribution_display(self, obj):
        if not obj.condition_distribution:
            return '-'
        
        html_parts = ['<div style="margin-bottom: 10px;">']
        total = sum(obj.condition_distribution.values())
        
        for condition, count in obj.condition_distribution.items():
            percentage = (count / total) * 100
            html_parts.append(
                f'<div style="margin-bottom: 5px;">'
                f'{condition}: {count} times ({percentage:.1f}%)'
                f'<div style="background-color: #007bff; width: {percentage}%; '
                f'height: 10px; border-radius: 5px;"></div>'
                f'</div>'
            )
        
        html_parts.append('</div>')
        return format_html(''.join(html_parts))
    condition_distribution_display.short_description = 'Condition Distribution'
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('city', 'date')
        }),
        ('Temperature Statistics', {
            'fields': (
                'min_temperature',
                'avg_temperature',
                'max_temperature'
            )
        }),
        ('Weather Conditions', {
            'fields': (
                'dominant_condition',
                'condition_distribution_display',
                'sample_count'
            )
        })
    )

    def has_add_permission(self, request):
        # Prevent manual addition of summaries as they're auto-generated
        return False