from supabase import create_client, Client
from flask import current_app
from datetime import datetime
import pytz

class SupabaseService:
    def __init__(self):
        self.client = None
    
    def get_client(self):
        """Get or create Supabase client"""
        if self.client is None:
            url = current_app.config.get('SUPABASE_URL')
            key = current_app.config.get('SUPABASE_KEY')
            if url and key:
                self.client = create_client(url, key)
        return self.client
    
    def _ph_time(self):
        """Get current Philippine time as string without timezone"""
        ph_tz = pytz.timezone('Asia/Manila')
        now_ph = datetime.now(ph_tz)
        return now_ph.strftime('%Y-%m-%dT%H:%M:%S')
    
    def save_weather_reading(self, location_name, latitude, longitude, temperature, humidity, heat_index, risk_level):
        """Save weather reading to Supabase"""
        client = self.get_client()
        if client is None:
            print("⚠️ Supabase not configured, skipping cloud save")
            return False
        
        try:
            data = {
                'location_name': location_name,
                'latitude': latitude,
                'longitude': longitude,
                'temperature': temperature,
                'humidity': humidity,
                'heat_index': heat_index,
                'risk_level': risk_level,
                'timestamp': self._ph_time()
            }
            client.table('weather_readings').insert(data).execute()
            return True
        except Exception as e:
            print(f"Supabase error: {e}")
            return False
    
    def save_alert_log(self, location_name, risk_level, temperature, humidity, message, email_sent):
        """Save alert log to Supabase"""
        client = self.get_client()
        if client is None:
            return False
        
        try:
            data = {
                'location_name': location_name,
                'risk_level': risk_level,
                'temperature': temperature,
                'humidity': humidity,
                'message': message,
                'email_sent': email_sent,
                'timestamp': self._ph_time()
            }
            client.table('alert_logs').insert(data).execute()
            return True
        except Exception as e:
            print(f"Supabase error: {e}")
            return False