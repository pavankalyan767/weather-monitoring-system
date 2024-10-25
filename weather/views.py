# views.py
from django.shortcuts import render
from django.views.generic import TemplateView
from django.http import JsonResponse
from django.utils import timezone
from datetime import timedelta
from .models import City, WeatherData, DailyWeatherSummary, WeatherAlert


import requests
import os
from dotenv import load_dotenv



# Load environment variables
load_dotenv()
OPENWEATHER_API_KEY = os.getenv('OPENWEATHER_API_KEY')









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
                'units': 'metric'  # Use 'imperial' for Fahrenheit
            })
            
            if response.status_code == 200:
                data = response.json()
                temperature = data['main']['temp']
                feels_like = data['main']['feels_like']
                condition = data['weather'][0]['description']
                
                # Store the data in the database
                weather = WeatherData.objects.create(
                    city=city,
                    temperature=temperature,
                    feels_like=feels_like,
                    condition=condition
                )
            else:
                print(f"Error fetching data for {city.name}: {response.status_code}")
                continue  # Skip to the next city if there's an error

        city_weather_data.append({
            'city': {
                'id': city.id,
                'name': city.name
            },
            'temperature': weather.temperature,
            'feels_like': weather.feels_like,
            'condition': weather.condition,
            'timestamp': weather.timestamp.isoformat()
        })
        
        # Get historical data for charts (last hour)
        hour_ago = timezone.now() - timedelta(hours=1)
        historical = WeatherData.objects.filter(
            city=city,
            timestamp__gte=hour_ago
        ).order_by('timestamp')
        
        historical_data[city.id] = [{
            'time': entry.timestamp.strftime('%H:%M'),
            'temperature': entry.temperature
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
                'avg_temperature': summary.avg_temperature
            }
    
    # Get active alerts
    active_alerts = [{
        'city': {'id': alert.city.id, 'name': alert.city.name},
        'message': alert.message,
        'timestamp': alert.timestamp.isoformat()
    } for alert in WeatherAlert.objects.filter(is_active=True)]
    
    return JsonResponse({
        'active_alerts': active_alerts,
        'city_weather_data': city_weather_data,
        'daily_summaries': daily_summaries,
        'historical_data': historical_data
    })



from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json

# A simple in-memory storage for alerts
# In a production application, you might want to use a database model
active_alerts = []
import random
def get_mock_current_temperature(city_id):
    # Simulate getting the current temperature for a given city.
    # In a real application, you would replace this with actual data fetching logic.
    return random.uniform(15, 35)  # Random temperature between 15°C and 35°C

from django.views.decorators.csrf import csrf_exempt
import json

@csrf_exempt  # Only use this for testing; consider CSRF protection for production
def subscribe_alert(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            city_id = data.get('cityId')
            threshold = data.get('threshold')

            # Perform validation and subscription logic here
            # ...

            # Example of returning success
            return JsonResponse({'success': True, 'alert': {'city_id': city_id, 'threshold': threshold}}, status=200)
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=400)
    return JsonResponse({'success': False, 'error': 'Invalid request method.'}, status=405)
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

        # Fetch active alerts
        active_alerts = WeatherAlert.objects.filter(is_active=True)
        context['cities'] = cities
        context['active_alerts'] = active_alerts  # Add this line to include alerts

        return context





