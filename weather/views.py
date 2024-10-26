from django.shortcuts import render
from django.views.generic import TemplateView
from django.http import JsonResponse
from django.utils import timezone
from datetime import timedelta
from .models import City, WeatherData, DailyWeatherSummary
import requests
import os
from dotenv import load_dotenv
from django.db.models import Avg, Max, Min, Count
from collections import Counter

# Load environment variables
load_dotenv()
OPENWEATHER_API_KEY = os.getenv('OPENWEATHER_API_KEY')

def update_daily_summary(city, date):
    """Update daily weather summary for a given city and date"""
    daily_data = WeatherData.objects.filter(
        city=city,
        timestamp__date=date
    )
    
    if daily_data.exists():
        # Calculate statistics
        stats = daily_data.aggregate(
            avg_temp=Avg('temperature'),
            max_temp=Max('temperature'),
            min_temp=Min('temperature')
        )
        
        # Calculate dominant condition
        conditions = daily_data.values_list('condition', flat=True)
        condition_counts = Counter(conditions)
        dominant_condition = max(condition_counts.items(), key=lambda x: x[1])[0]
        
        # Update or create daily summary
        summary, created = DailyWeatherSummary.objects.update_or_create(
            city=city,
            date=date,
            defaults={
                'avg_temperature': stats['avg_temp'],
                'max_temperature': stats['max_temp'],
                'min_temperature': stats['min_temp'],
                'dominant_condition': dominant_condition,
                'condition_distribution': dict(condition_counts),
                'sample_count': len(conditions)
            }
        )
        return summary
    return None

def fetch_weather_data(request):
    """API endpoint to fetch updated weather data."""
    cities = City.objects.all()
    
    # Format for frontend consumption
    city_weather_data = []
    historical_data = {}
    daily_summaries = {}
    
    for city in cities:
        # Get latest weather
        weather = WeatherData.objects.filter(city=city).order_by('-timestamp').first()
        
        # Check if the last update was more than 1 minute ago
        if not weather or (timezone.now() - weather.timestamp) > timedelta(minutes=1):
            # Fetch new weather data from OpenWeather API
            OPENWEATHER_URL = 'http://api.openweathermap.org/data/2.5/weather'
            response = requests.get(OPENWEATHER_URL, params={
                'q': city.name,
                'appid': OPENWEATHER_API_KEY,
                'units': 'metric'
            })
            
            if response.status_code == 200:
                data = response.json()
                weather = WeatherData.objects.create(
                    city=city,
                    temperature=data['main']['temp'],
                    feels_like=data['main']['feels_like'],
                    condition=data['weather'][0]['description'],
                    humidity=data['main']['humidity'],
                    wind_speed=data['wind']['speed']
                )
                
                # Update daily summary
                update_daily_summary(city, timezone.now().date())
            else:
                print(f"Error fetching data for {city.name}: {response.status_code}")
                continue

        # Prepare current weather data
        city_weather_data.append({
            'city': {
                'id': city.id,
                'name': city.name
            },
            'temperature': weather.temperature,
            'feels_like': weather.feels_like,
            'condition': weather.condition,
            'humidity': weather.humidity,
            'wind_speed': weather.wind_speed,
            'timestamp': weather.timestamp.isoformat()
        })
        
        # Get historical data for charts (last 24 hours)
        day_ago = timezone.now() - timedelta(hours=24)
        historical = WeatherData.objects.filter(
            city=city,
            timestamp__gte=day_ago
        ).order_by('timestamp')
        
        historical_data[city.id] = [{
            'time': entry.timestamp.strftime('%H:%M'),
            'temperature': entry.temperature,
            'humidity': entry.humidity,
            'wind_speed': entry.wind_speed
        } for entry in historical]
        
        # Get daily summary
        summary = DailyWeatherSummary.objects.filter(
            city=city,
            date=timezone.now().date()
        ).first()
        
        if summary:
            daily_summaries[city.id] = {
                'max_temperature': summary.max_temperature,
                'min_temperature': summary.min_temperature,
                'avg_temperature': summary.avg_temperature,
                'dominant_condition': summary.dominant_condition,
                'condition_distribution': summary.condition_distribution,
                'sample_count': summary.sample_count
            }
    
    return JsonResponse({
        'city_weather_data': city_weather_data,
        'daily_summaries': daily_summaries,
        'historical_data': historical_data
    })

class DashboardView(TemplateView):
    template_name = 'weather/dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        cities = City.objects.all()

        # Initialize default cities if none exist
        if not cities.exists():
            default_cities = [
                {'name': 'Delhi', 'latitude': 28.6139, 'longitude': 77.2090},
                {'name': 'Mumbai', 'latitude': 19.0760, 'longitude': 72.8777},
                {'name': 'Chennai', 'latitude': 13.0827, 'longitude': 80.2707},
                {'name': 'Bangalore', 'latitude': 12.9716, 'longitude': 77.5946},
                {'name': 'Kolkata', 'latitude': 22.5726, 'longitude': 88.3639},
                {'name': 'Hyderabad', 'latitude': 17.3850, 'longitude': 78.4867},
            ]
            for city_data in default_cities:
                City.objects.get_or_create(**city_data)
            cities = City.objects.all()

        context['cities'] = cities
        return context