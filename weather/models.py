# models.py
from django.db import models
from django.utils import timezone

class City(models.Model):
    name = models.CharField(max_length=100)
    latitude = models.FloatField()
    longitude = models.FloatField()
    
    class Meta:
        verbose_name_plural = 'cities'
    
    def __str__(self):
        return self.name

class WeatherData(models.Model):
    city = models.ForeignKey(City, on_delete=models.CASCADE)
    temperature = models.FloatField()
    feels_like = models.FloatField()
    condition = models.CharField(max_length=100)
    humidity = models.FloatField(default=0)
    wind_speed = models.FloatField(default=0)
    timestamp = models.DateTimeField(default=timezone.now)
    
    class Meta:
        indexes = [
            models.Index(fields=['city', 'timestamp']),
        ]
    
    def __str__(self):
        return f"{self.city.name} - {self.temperature}°C - {self.condition}"

class DailyWeatherSummary(models.Model):
    city = models.ForeignKey(City, on_delete=models.CASCADE)
    date = models.DateField()
    avg_temperature = models.FloatField()
    max_temperature = models.FloatField()
    min_temperature = models.FloatField()
    dominant_condition = models.CharField(max_length=100)
    condition_distribution = models.JSONField(default=dict)
    sample_count = models.IntegerField(default=0)
    
    class Meta:
        unique_together = ['city', 'date']
        verbose_name_plural = 'daily weather summaries'
    
    def __str__(self):
        return f"{self.city.name} - {self.date}"