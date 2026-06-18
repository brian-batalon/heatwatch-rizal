from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from config import Config
from apscheduler.schedulers.background import BackgroundScheduler
import atexit

db = SQLAlchemy()

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # Initialize extensions
    db.init_app(app)
    
    # Set default ML model
    app.config['CURRENT_ML_MODEL'] = 'rf'
    
    # Register blueprints
    from app.routes import main
    app.register_blueprint(main)
    
    # Create database tables
    with app.app_context():
        db.create_all()
    
    # Background weather fetcher (every 6 hours)
    def fetch_weather_job():
        with app.app_context():
            from app.weather_service import WeatherService
            from app.risk_classifier import RiskClassifier
            from app.models import WeatherReading, AlertLog
            from app.supabase_service import SupabaseService
            
            print("📡 Background weather fetch starting...")
            ws = WeatherService()
            locations = app.config['MONITORED_LOCATIONS']
            weather_data = ws.fetch_multiple_locations(locations)
            
            rc = RiskClassifier(app.config['HEAT_RISK_THRESHOLDS'])
            ss = SupabaseService()
            
            for data in weather_data:
                if data['success']:
                    hi = rc.calculate_heat_index(data['temperature'], data['humidity'])
                    rl = rc.classify_risk_rule_based(data['temperature'], data['humidity'])
                    ri = rc.get_risk_description(rl)
                    
                    reading = WeatherReading(
                        location_name=data['name'], latitude=data['lat'], longitude=data['lon'],
                        temperature=data['temperature'], humidity=data['humidity'],
                        heat_index=hi, risk_level=rl
                    )
                    db.session.add(reading)
                    
                    if rl in ['HIGH', 'DANGEROUS']:
                        alert_log = AlertLog(
                            location_name=data['name'], risk_level=rl,
                            temperature=data['temperature'], humidity=data['humidity'],
                            message=ri['description'], email_sent=False
                        )
                        db.session.add(alert_log)
                    
                    try:
                        ss.save_weather_reading(data['name'], data['lat'], data['lon'],
                            data['temperature'], data['humidity'], hi, rl)
                        if rl in ['HIGH', 'DANGEROUS']:
                            ss.save_alert_log(data['name'], rl, data['temperature'],
                                data['humidity'], ri['description'], False)
                    except Exception as e:
                        print(f"Supabase background save error: {e}")
            
            db.session.commit()
            print(f"📡 Background weather fetch completed ({len(weather_data)} locations)")
    
    # Start scheduler
    scheduler = BackgroundScheduler()
    scheduler.add_job(fetch_weather_job, 'interval', hours=6)
    scheduler.start()
    atexit.register(lambda: scheduler.shutdown())
    
    print("⏰ Background scheduler started (every 6 hours)")
    
    return app