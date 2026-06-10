from datetime import datetime, timedelta
from app import db

class WeatherReading(db.Model):
    __tablename__ = 'weather_readings'
    
    id = db.Column(db.Integer, primary_key=True)
    location_name = db.Column(db.String(100), nullable=False)
    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)
    temperature = db.Column(db.Float, nullable=False)
    humidity = db.Column(db.Float, nullable=False)
    heat_index = db.Column(db.Float)
    risk_level = db.Column(db.String(20), nullable=False)
    timestamp = db.Column(db.DateTime, default=lambda: datetime.utcnow() + timedelta(hours=8))
    
    def __repr__(self):
        return f'<WeatherReading {self.location_name} - {self.temperature}°C - {self.risk_level}>'

class AlertLog(db.Model):
    __tablename__ = 'alert_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    location_name = db.Column(db.String(100), nullable=False)
    risk_level = db.Column(db.String(20), nullable=False)
    temperature = db.Column(db.Float, nullable=False)
    humidity = db.Column(db.Float, nullable=False)
    message = db.Column(db.Text, nullable=False)
    email_sent = db.Column(db.Boolean, default=False)
    timestamp = db.Column(db.DateTime, default=lambda: datetime.utcnow() + timedelta(hours=8))
    
    def __repr__(self):
        return f'<AlertLog {self.location_name} - {self.risk_level} - {self.timestamp}>'