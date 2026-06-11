import requests
from datetime import datetime, timedelta
import time

# Simple cache
_cache = {
    'data': None,
    'timestamp': None
}

class WeatherService:
    def __init__(self, api_url="https://api.open-meteo.com/v1/forecast"):
        self.api_url = api_url
        self.cache_duration = 600  # Cache for 10 minutes
    
    def fetch_current_weather(self, lat, lon):
        """Fetch current weather data for given coordinates"""
        params = {
            'latitude': lat,
            'longitude': lon,
            'current': 'temperature_2m,relative_humidity_2m',
            'timezone': 'Asia/Manila'
        }
        
        try:
            response = requests.get(self.api_url, params=params, timeout=20)
            response.raise_for_status()
            data = response.json()
            
            return {
                'temperature': data['current']['temperature_2m'],
                'humidity': data['current']['relative_humidity_2m'],
                'timestamp': datetime.utcnow() + timedelta(hours=8),
                'success': True
            }
        except requests.exceptions.RequestException as e:
            print(f"Error fetching weather: {e}")
            return {
                'temperature': None,
                'humidity': None,
                'timestamp': datetime.utcnow() + timedelta(hours=8),
                'success': False,
                'error': str(e)
            }
    
    def fetch_multiple_locations(self, locations):
        """Fetch weather data one at a time with caching and retry"""
        
        # Check cache
        if _cache['data'] is not None and _cache['timestamp'] is not None:
            age = (datetime.utcnow() + timedelta(hours=8) - _cache['timestamp']).total_seconds()
            if age < self.cache_duration:
                print(f"📦 Using cached data ({int(age)}s old)")
                return _cache['data']
        
        print("🔄 Fetching fresh weather data (sequential with retry)...")
        results = []
        
        for i, loc in enumerate(locations):
            print(f"  📡 {i+1}/{len(locations)}: {loc['name']}")
            weather = self.fetch_current_weather(loc['lat'], loc['lon'])
            
            # Retry once if failed
            if not weather['success']:
                time.sleep(1)
                print(f"  🔄 Retrying {loc['name']}...")
                weather = self.fetch_current_weather(loc['lat'], loc['lon'])
            
            results.append({
                'name': loc['name'],
                'lat': loc['lat'],
                'lon': loc['lon'],
                'temperature': weather['temperature'],
                'humidity': weather['humidity'],
                'timestamp': weather['timestamp'],
                'success': weather['success']
            })
            time.sleep(0.5)
        
        # Save to cache
        _cache['data'] = results
        _cache['timestamp'] = datetime.utcnow() + timedelta(hours=8)
        
        # Count success
        success_count = sum(1 for r in results if r['success'])
        print(f"✅ Loaded {success_count}/{len(results)} locations")
        return results