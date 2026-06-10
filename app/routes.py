from flask import Blueprint, render_template, jsonify, request, current_app
from app.models import WeatherReading, AlertLog
from app.weather_service import WeatherService
from app.risk_classifier import RiskClassifier
from app.email_service import EmailService
from app.supabase_service import SupabaseService
from app import db
from datetime import datetime, timedelta
import os
import json

main = Blueprint('main', __name__)

@main.route('/')
def index():
    """Dashboard home page"""
    return render_template('dashboard.html', title='Dashboard')

@main.route('/map')
def map_view():
    """Interactive map page"""
    return render_template('map.html', title='Heat Risk Map')

@main.route('/analytics')
def analytics():
    """Analytics and charts page"""
    return render_template('analytics.html', title='Analytics')

@main.route('/alerts')
def alerts():
    """Alert history page"""
    return render_template('alerts.html', title='Alert Logs')

@main.route('/models')
def models_page():
    """ML Models comparison page"""
    return render_template('models.html', title='ML Models')

@main.route('/history')
def history():
    """Weather history page"""
    return render_template('history.html', title='History')

@main.route('/api/current-weather')
def get_current_weather():
    """API endpoint to fetch current weather for all monitored locations"""
    from app.ml_model import HeatRiskMLModel
    
    locations = current_app.config['MONITORED_LOCATIONS']
    thresholds = current_app.config['HEAT_RISK_THRESHOLDS']
    
    weather_service = WeatherService()
    risk_classifier = RiskClassifier(thresholds)
    
    # Read saved model preference from file
    model_file = os.path.join(current_app.instance_path, 'current_model.json')
    current_model = 'rf'
    if os.path.exists(model_file):
        with open(model_file, 'r') as f:
            saved = json.load(f)
            current_model = saved.get('model', 'rf')
    
    ml_model = HeatRiskMLModel(current_model)
    
    # Fetch weather data
    weather_data = weather_service.fetch_multiple_locations(locations)
    
    # Process and classify risk
    results = []
    for data in weather_data:
        if data['success']:
            heat_index = risk_classifier.calculate_heat_index(data['temperature'], data['humidity'])
            
            # Current risk from rule-based classifier
            risk_level = risk_classifier.classify_risk_rule_based(data['temperature'], data['humidity'])
            
            # Get ML forecast (predicted temperature 6h ahead)
            predicted_temp, predicted_risk = ml_model.predict_temperature(
                data['temperature'], data['humidity'], heat_index
            )
            
            risk_info = risk_classifier.get_risk_description(risk_level)
            
            result = {
                'name': data['name'],
                'lat': data['lat'],
                'lon': data['lon'],
                'temperature': data['temperature'],
                'humidity': data['humidity'],
                'heat_index': heat_index,
                'risk_level': risk_level,
                'risk_color': risk_info['color'],
                'risk_description': risk_info['description'],
                'predicted_temp': predicted_temp,
                'predicted_risk': predicted_risk,
                'timestamp': data['timestamp'].isoformat(),
                'success': True
            }
            
            # Save to database
            reading = WeatherReading(
                location_name=data['name'],
                latitude=data['lat'],
                longitude=data['lon'],
                temperature=data['temperature'],
                humidity=data['humidity'],
                heat_index=heat_index,
                risk_level=risk_level
            )
            db.session.add(reading)
            
            # Also save to Supabase
            try:
                supabase_service = SupabaseService()
                supabase_service.save_weather_reading(
                    location_name=data['name'],
                    latitude=data['lat'],
                    longitude=data['lon'],
                    temperature=data['temperature'],
                    humidity=data['humidity'],
                    heat_index=heat_index,
                    risk_level=risk_level
                )
            except Exception as e:
                print(f"Supabase save error: {e}")
        else:
            result = {
                'name': data['name'],
                'lat': data['lat'],
                'lon': data['lon'],
                'temperature': None,
                'humidity': None,
                'heat_index': None,
                'risk_level': 'UNKNOWN',
                'risk_color': '#6b7280',
                'risk_description': 'Data unavailable',
                'predicted_temp': None,
                'predicted_risk': None,
                'timestamp': data['timestamp'].isoformat(),
                'success': False
            }
        
        results.append(result)
    
    db.session.commit()
    
    return jsonify(results)

@main.route('/api/recent-readings')
def get_recent_readings():
    """API endpoint to get recent weather readings"""
    limit = request.args.get('limit', 50, type=int)
    readings = WeatherReading.query.order_by(WeatherReading.timestamp.desc()).limit(limit).all()
    
    data = []
    for r in readings:
        data.append({
            'id': r.id,
            'location_name': r.location_name,
            'temperature': r.temperature,
            'humidity': r.humidity,
            'heat_index': r.heat_index,
            'risk_level': r.risk_level,
            'timestamp': r.timestamp.isoformat()
        })
    
    return jsonify(data)

@main.route('/api/alert-history')
def get_alert_history():
    """API endpoint to get alert history"""
    limit = request.args.get('limit', 50, type=int)
    alerts = AlertLog.query.order_by(AlertLog.timestamp.desc()).limit(limit).all()
    
    data = []
    for a in alerts:
        data.append({
            'id': a.id,
            'location_name': a.location_name,
            'risk_level': a.risk_level,
            'temperature': a.temperature,
            'humidity': a.humidity,
            'message': a.message,
            'email_sent': a.email_sent,
            'timestamp': a.timestamp.isoformat()
        })
    
    return jsonify(data)

@main.route('/api/stats')
def get_stats():
    """API endpoint to get statistics for analytics"""
    yesterday = datetime.utcnow() - timedelta(hours=24)
    readings = WeatherReading.query.filter(WeatherReading.timestamp >= yesterday).all()
    
    if not readings:
        return jsonify({'message': 'No data available'})
    
    locations = {}
    risk_counts = {'NORMAL': 0, 'MODERATE': 0, 'HIGH': 0, 'DANGEROUS': 0, 'UNKNOWN': 0}
    temperatures = []
    humidities = []
    
    for r in readings:
        if r.location_name not in locations:
            locations[r.location_name] = {'temps': [], 'humidity': [], 'risk_levels': []}
        
        locations[r.location_name]['temps'].append(r.temperature)
        locations[r.location_name]['humidity'].append(r.humidity)
        locations[r.location_name]['risk_levels'].append(r.risk_level)
        
        risk_counts[r.risk_level] = risk_counts.get(r.risk_level, 0) + 1
        temperatures.append(r.temperature)
        humidities.append(r.humidity)
    
    location_stats = []
    for name, data in locations.items():
        if data['temps']:
            location_stats.append({
                'name': name,
                'avg_temp': round(sum(data['temps']) / len(data['temps']), 1),
                'max_temp': round(max(data['temps']), 1),
                'avg_humidity': round(sum(data['humidity']) / len(data['humidity']), 1)
            })
    
    stats = {
        'total_readings': len(readings),
        'avg_temperature': round(sum(temperatures) / len(temperatures), 1) if temperatures else 0,
        'max_temperature': round(max(temperatures), 1) if temperatures else 0,
        'avg_humidity': round(sum(humidities) / len(humidities), 1) if humidities else 0,
        'risk_counts': risk_counts,
        'location_stats': sorted(location_stats, key=lambda x: x['max_temp'], reverse=True)[:5]
    }
    
    return jsonify(stats)

@main.route('/api/send-alert', methods=['POST'])
def send_custom_alert():
    """API endpoint to manually send alert to any email"""
    data = request.get_json()
    
    recipient_email = data.get('email')
    location_name = data.get('location')
    temperature = data.get('temperature')
    humidity = data.get('humidity')
    risk_level = data.get('risk_level')
    heat_index = data.get('heat_index')
    predicted_temp = data.get('predicted_temp')
    predicted_risk = data.get('predicted_risk')
    
    if not recipient_email or not location_name:
        return jsonify({'success': False, 'message': 'Email and location are required'}), 400
    
    email_service = EmailService()
    sent = email_service.send_custom_alert(
        recipient=recipient_email,
        location_name=location_name,
        temperature=temperature,
        humidity=humidity,
        risk_level=risk_level,
        heat_index=heat_index,
        predicted_temp=predicted_temp,
        predicted_risk=predicted_risk
    )
    
    if sent:
        return jsonify({'success': True, 'message': f'Alert sent to {recipient_email}'})
    else:
        return jsonify({'success': False, 'message': 'Failed to send email'}), 500

@main.route('/api/model-info')
def get_model_info():
    """API endpoint to get ML model information"""
    from app.ml_model import HeatRiskMLModel
    
    model_file = os.path.join(current_app.instance_path, 'current_model.json')
    current_model = 'rf'
    if os.path.exists(model_file):
        with open(model_file, 'r') as f:
            saved = json.load(f)
            current_model = saved.get('model', 'rf')
    
    ml_model = HeatRiskMLModel(current_model)
    info = ml_model.get_model_info()
    
    return jsonify(info)

@main.route('/api/switch-model', methods=['POST'])
def switch_model():
    """API endpoint to switch ML model"""
    data = request.get_json()
    model_name = data.get('model', 'rf')
    
    from app.ml_model import HeatRiskMLModel
    
    ml_model = HeatRiskMLModel()
    success = ml_model.switch_model(model_name)
    
    model_file = os.path.join(current_app.instance_path, 'current_model.json')
    with open(model_file, 'w') as f:
        json.dump({'model': model_name}, f)
    
    return jsonify({'success': success, 'model': model_name, 'message': f'Switched to {model_name} model' if success else 'Failed to switch model'})