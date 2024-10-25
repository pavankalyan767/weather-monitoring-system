# Generated by Django 4.2.16 on 2024-10-26 13:34

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('weather', '0003_remove_weatheralert_city_delete_alertconfiguration_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='AlertThreshold',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('alert_type', models.CharField(choices=[('TEMP_HIGH', 'High Temperature'), ('TEMP_LOW', 'Low Temperature'), ('HUMIDITY', 'High Humidity'), ('WIND_SPEED', 'High Wind Speed')], max_length=20)),
                ('threshold_value', models.FloatField()),
                ('consecutive_checks', models.IntegerField(default=2)),
                ('is_active', models.BooleanField(default=True)),
            ],
        ),
        migrations.AddField(
            model_name='city',
            name='last_update',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='city',
            name='update_interval',
            field=models.IntegerField(default=5, help_text='Update interval in minutes'),
        ),
        migrations.CreateModel(
            name='WeatherAlert',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('current_value', models.FloatField()),
                ('consecutive_count', models.IntegerField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('is_active', models.BooleanField(default=True)),
                ('threshold', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='weather.alertthreshold')),
            ],
        ),
        migrations.AddField(
            model_name='alertthreshold',
            name='city',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='weather.city'),
        ),
    ]
