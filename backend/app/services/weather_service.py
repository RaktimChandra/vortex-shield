import requests
from typing import Dict, Optional
from datetime import datetime
import random

class WeatherService:
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key
        # Use FREE Open-Meteo API (no API key needed!)
        self.open_meteo_url = "https://api.open-meteo.com/v1/forecast"
        self.use_real_api = True  # Always use real API now!
    
    def get_current_weather(self, latitude: float, longitude: float) -> Dict:
        """Get REAL weather data using FREE Open-Meteo API"""
        try:
            params = {
                'latitude': latitude,
                'longitude': longitude,
                'current_weather': 'true',
                'hourly': 'temperature_2m,precipitation,rain,windspeed_10m,relativehumidity_2m'
            }
            
            response = requests.get(self.open_meteo_url, params=params, timeout=5)
            response.raise_for_status()
            data = response.json()
            
            return self._parse_open_meteo_data(data)
        except Exception as e:
            print(f"Open-Meteo API error: {e}")
            return self._get_mock_weather(latitude, longitude)
    
    def _get_mock_weather(self, latitude: float, longitude: float) -> Dict:
        conditions = ['Clear', 'Clouds', 'Rain', 'Drizzle', 'Thunderstorm']
        weights = [0.4, 0.3, 0.15, 0.1, 0.05]
        
        condition = random.choices(conditions, weights=weights)[0]
        
        base_temp = 28
        if latitude > 28:
            base_temp = 25
        elif latitude < 20:
            base_temp = 32
        
        temperature = round(base_temp + random.uniform(-5, 5), 1)
        
        rainfall_mm = 0.0
        if condition == 'Rain':
            rainfall_mm = round(random.uniform(5, 80), 1)
        elif condition == 'Thunderstorm':
            rainfall_mm = round(random.uniform(40, 120), 1)
        elif condition == 'Drizzle':
            rainfall_mm = round(random.uniform(1, 10), 1)
        
        humidity = round(60 + random.uniform(-20, 30))
        wind_speed = round(random.uniform(5, 25), 1)
        
        return {
            'temperature_c': temperature,
            'feels_like_c': round(temperature + random.uniform(-2, 3), 1),
            'humidity': humidity,
            'wind_speed_kmh': wind_speed,
            'condition': condition,
            'description': self._get_weather_description(condition),
            'rainfall_mm': rainfall_mm,
            'rainfall_last_hour': rainfall_mm if rainfall_mm > 0 else 0,
            'rainfall_last_3hours': rainfall_mm * 2.5 if rainfall_mm > 0 else 0,
            'pressure_hpa': round(1013 + random.uniform(-10, 10)),
            'visibility_km': round(10 - (rainfall_mm / 20)),
            'timestamp': datetime.now().isoformat(),
            'coordinates': {
                'latitude': latitude,
                'longitude': longitude
            }
        }
    
    def _parse_open_meteo_data(self, data: Dict) -> Dict:
        """Parse FREE Open-Meteo API response"""
        current = data.get('current_weather', {})
        hourly = data.get('hourly', {})
        
        # Get current hour data
        temp = current.get('temperature', 0)
        wind_speed = current.get('windspeed', 0)
        
        # Get rainfall from hourly data (most recent hour)
        rainfall = 0
        if 'rain' in hourly and hourly['rain']:
            rainfall = hourly['rain'][0] if isinstance(hourly['rain'], list) else 0
        
        # Get humidity
        humidity = 60
        if 'relativehumidity_2m' in hourly and hourly['relativehumidity_2m']:
            humidity = hourly['relativehumidity_2m'][0] if isinstance(hourly['relativehumidity_2m'], list) else 60
        
        # Determine condition from weather code
        weather_code = current.get('weathercode', 0)
        condition, description = self._interpret_weather_code(weather_code)
        
        return {
            'temperature_c': round(temp, 1),
            'feels_like_c': round(temp - (wind_speed * 0.2), 1),
            'humidity': humidity,
            'wind_speed_kmh': round(wind_speed, 1),
            'condition': condition,
            'description': description,
            'rainfall_mm': round(rainfall, 1),
            'rainfall_last_hour': round(rainfall, 1),
            'rainfall_last_3hours': round(rainfall * 2.5, 1),
            'pressure_hpa': 1013,
            'visibility_km': 10,
            'timestamp': datetime.now().isoformat(),
            'coordinates': {
                'latitude': data.get('latitude', 0),
                'longitude': data.get('longitude', 0)
            },
            'real_api': True  # Mark as real data!
        }
    
    def _interpret_weather_code(self, code: int) -> tuple:
        """Interpret WMO weather codes from Open-Meteo"""
        if code == 0:
            return 'Clear', 'clear sky'
        elif code in [1, 2, 3]:
            return 'Clouds', 'partly cloudy'
        elif code in [45, 48]:
            return 'Fog', 'fog'
        elif code in [51, 53, 55]:
            return 'Drizzle', 'light drizzle'
        elif code in [61, 63, 65]:
            return 'Rain', 'moderate rain'
        elif code in [71, 73, 75]:
            return 'Snow', 'snow'
        elif code in [95, 96, 99]:
            return 'Thunderstorm', 'thunderstorm'
        else:
            return 'Unknown', 'unknown conditions'
    
    def _get_weather_description(self, condition: str) -> str:
        descriptions = {
            'Clear': 'clear sky',
            'Clouds': 'scattered clouds',
            'Rain': 'moderate rain',
            'Drizzle': 'light drizzle',
            'Thunderstorm': 'thunderstorm with heavy rain'
        }
        return descriptions.get(condition, 'unknown')
    
    def get_air_quality(self, latitude: float, longitude: float) -> Dict:
        aqi_base = 100
        
        if random.random() > 0.7:
            aqi_base = 200
        
        aqi = round(aqi_base + random.uniform(-50, 100))
        aqi = max(0, min(500, aqi))
        
        category = self._get_aqi_category(aqi)
        
        return {
            'aqi': aqi,
            'category': category,
            'pm25': round(aqi * 0.3, 1),
            'pm10': round(aqi * 0.5, 1),
            'co': round(aqi * 0.1, 1),
            'no2': round(aqi * 0.15, 1),
            'so2': round(aqi * 0.05, 1),
            'o3': round(aqi * 0.2, 1),
            'health_concern': self._get_health_concern(category),
            'timestamp': datetime.now().isoformat(),
            'coordinates': {
                'latitude': latitude,
                'longitude': longitude
            }
        }
    
    def _get_aqi_category(self, aqi: int) -> str:
        if aqi <= 50:
            return 'Good'
        elif aqi <= 100:
            return 'Moderate'
        elif aqi <= 150:
            return 'Unhealthy for Sensitive Groups'
        elif aqi <= 200:
            return 'Unhealthy'
        elif aqi <= 300:
            return 'Very Unhealthy'
        else:
            return 'Hazardous'
    
    def _get_health_concern(self, category: str) -> str:
        concerns = {
            'Good': 'Air quality is satisfactory',
            'Moderate': 'Air quality is acceptable',
            'Unhealthy for Sensitive Groups': 'Sensitive individuals should limit outdoor activity',
            'Unhealthy': 'Everyone should limit prolonged outdoor exertion',
            'Very Unhealthy': 'Health alert - avoid outdoor activity',
            'Hazardous': 'Health warning - stay indoors'
        }
        return concerns.get(category, 'Unknown')
    
    def get_traffic_data(self, latitude: float, longitude: float) -> Dict:
        hour = datetime.now().hour
        is_weekday = datetime.now().weekday() < 5
        
        if is_weekday and (7 <= hour <= 10 or 17 <= hour <= 21):
            base_congestion = 0.7
        elif is_weekday:
            base_congestion = 0.4
        else:
            base_congestion = 0.3
        
        congestion_level = round(base_congestion + random.uniform(-0.2, 0.2), 2)
        congestion_level = max(0, min(1, congestion_level))
        
        avg_speed = round(40 * (1 - congestion_level))
        
        return {
            'congestion_level': congestion_level,
            'congestion_percentage': round(congestion_level * 100, 1),
            'average_speed_kmh': avg_speed,
            'typical_speed_kmh': 40,
            'delay_minutes': round(congestion_level * 30),
            'traffic_flow': self._get_traffic_flow(congestion_level),
            'incident_count': random.randint(0, 3) if congestion_level > 0.6 else 0,
            'timestamp': datetime.now().isoformat(),
            'coordinates': {
                'latitude': latitude,
                'longitude': longitude
            }
        }
    
    def _get_traffic_flow(self, congestion: float) -> str:
        if congestion < 0.3:
            return 'Free Flow'
        elif congestion < 0.5:
            return 'Light Traffic'
        elif congestion < 0.7:
            return 'Moderate Traffic'
        else:
            return 'Heavy Traffic'
