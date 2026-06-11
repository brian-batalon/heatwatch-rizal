import requests
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor, as_completed

# Simple cache
_cache = {
    'data': None,
    'timestamp': None
}

class WeatherService:
    def __init__(self, api_url="https://api.open-meteo.com/v1/forecast"):
        self.api_url = api_url
        self.cache_duration = 120  # Cache for 2 minutes
    
    def fetch_current_weather(self, lat, lon):
        """Fetch current weather data for given coordinates"""
        params = {
            'latitude': lat,
            'longitude': lon,
            'current': 'temperature_2m,relative_humidity_2m',
            'timezone': 'Asia/Manila'
        }
        
        try:
            response = requests.get(self.api_url, params=params, timeout=15)
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
        """Fetch weather data for multiple locations IN PARALLEL, with caching"""
        
        # Check cache
        if _cache['data'] is not None and _cache['timestamp'] is not None:
            age = (datetime.utcnow() + timedelta(hours=8) - _cache['timestamp']).total_seconds()
            if age < self.cache_duration:
                print(f"📦 Using cached data ({int(age)}s old)")
                return _cache['data']
        
        print("🔄 Fetching fresh weather data...")
        results = []
        
        with ThreadPoolExecutor(max_workers=2) as executor:
            future_to_loc = {
                executor.submit(self.fetch_current_weather, loc['lat'], loc['lon']): loc 
                for loc in locations
            }
            
            for future in as_completed(future_to_loc):
                loc = future_to_loc[future]
                weather = future.result()
                results.append({
                    'name': loc['name'],
                    'lat': loc['lat'],
                    'lon': loc['lon'],
                    'temperature': weather['temperature'],
                    'humidity': weather['humidity'],
                    'timestamp': weather['timestamp'],
                    'success': weather['success']
                })
        
        # Save to cache
        _cache['data'] = results
        _cache['timestamp'] = datetime.utcnow() + timedelta(hours=8)
        
        return results