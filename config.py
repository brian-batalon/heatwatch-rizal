import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    
    # Database - Supabase PostgreSQL (Cloud)
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'postgresql://postgres.mrednkztgxydxqkedwng:HeatWatch2026@aws-1-ap-southeast-1.pooler.supabase.com:6543/postgres'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Supabase Configuration
    SUPABASE_URL = 'https://mrednkztgxydxqkedwng.supabase.co'
    SUPABASE_KEY = 'sb_publishable_0gqGZjBUfbL2LI2sznAO7w_EzJEUcQM'
    
    # Email Configuration
    MAIL_SERVER = os.environ.get('MAIL_SERVER') or 'smtp.gmail.com'
    MAIL_PORT = int(os.environ.get('MAIL_PORT') or 587)
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS') or True
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER')
    ALERT_RECIPIENT = os.environ.get('ALERT_RECIPIENT')
    
    # Weather API
    OPEN_METEO_API_URL = "https://api.open-meteo.com/v1/forecast"
    
    # Heat Risk Thresholds (Temperature in °C, Humidity in %)
    HEAT_RISK_THRESHOLDS = {
        'NORMAL': {'temp_max': 26},
        'MODERATE': {'temp_min': 27, 'temp_max': 32},
        'HIGH': {'temp_min': 33, 'temp_max': 41},
        'DANGEROUS': {'temp_min': 42}
    }
    
    # Default monitored locations - Rizal Province & nearby areas (latitude, longitude, name)
    MONITORED_LOCATIONS = [
        {'lat': 14.580077418195712, 'lon': 121.17125904641374, 'name': 'Antipolo City, Rizal'},
        {'lat': 14.552346099991396, 'lon': 121.12574794224656, 'name': 'Taytay, Rizal'},
        {'lat': 14.581327414523258, 'lon': 121.11552767258381, 'name': 'Cainta, Rizal'},
        {'lat': 14.531430615328725, 'lon': 121.15428846218407, 'name': 'Angono, Rizal'},
        {'lat': 14.483369536942085, 'lon': 121.18682578966428, 'name': 'Binangonan, Rizal'},
        {'lat': 14.484675857150314, 'lon': 121.23039201401565, 'name': 'Cardona, Rizal'},
        {'lat': 14.51272886764837, 'lon': 121.2381962742471, 'name': 'Morong, Rizal'},
        {'lat': 14.613424918288828, 'lon': 121.37659746832296, 'name': 'Tanay, Rizal'},
        {'lat': 14.434726126395958, 'lon': 121.33710500626552, 'name': 'Pililla, Rizal'},
        {'lat': 14.538404369022738, 'lon': 121.27464380767063, 'name': 'Baras, Rizal'},
        {'lat': 14.34578700015486, 'lon': 121.37653328304424, 'name': 'Jala-Jala, Rizal'},
        {'lat': 14.559391622834875, 'lon': 121.20727045082039, 'name': 'Teresa, Rizal'},
        {'lat': 14.69530104503483, 'lon': 121.11968284335471, 'name': 'San Mateo, Rizal'},
        {'lat': 14.732290719934118, 'lon': 121.14225736071755, 'name': 'Rodriguez (Montalban), Rizal'},
        {'lat': 14.599289838602981, 'lon': 120.98634910707935, 'name': 'Manila (Reference)'},
        {'lat': 14.634941538967677, 'lon': 121.10110324960077, 'name': 'Marikina City'},
        {'lat': 14.561286135988158, 'lon': 121.0778353969163, 'name': 'Pasig City'}
    ]