import numpy as np
from datetime import datetime

class RiskClassifier:
    def __init__(self, thresholds=None):
        # Temperature-based thresholds (humidity not used for classification)
        self.thresholds = {
            'NORMAL': {'temp_max': 26},
            'MODERATE': {'temp_min': 27, 'temp_max': 32},
            'HIGH': {'temp_min': 33, 'temp_max': 41},
            'DANGEROUS': {'temp_min': 42}
        }
    
    def calculate_heat_index(self, temperature, humidity):
        """Calculate heat index using NOAA formula"""
        if temperature is None or humidity is None:
            return None
        
        # Convert to Fahrenheit for formula
        T = (temperature * 9/5) + 32
        R = humidity
        
        # Heat index formula (NOAA)
        HI = 0.5 * (T + 61.0 + ((T - 68.0) * 1.2) + (R * 0.094))
        
        if HI >= 80:
            HI = -42.379 + 2.04901523 * T + 10.14333127 * R - 0.22475541 * T * R \
                 - 0.00683783 * T * T - 0.05481717 * R * R + 0.00122874 * T * T * R \
                 + 0.00085282 * T * R * R - 0.00000199 * T * T * R * R
        
        # Convert back to Celsius
        heat_index_c = (HI - 32) * 5/9
        return round(heat_index_c, 1)
    
    def classify_risk_rule_based(self, temperature, humidity):
        """Temperature-based heat risk classification"""
        if temperature is None:
            return 'UNKNOWN'
        
        if temperature >= 42:
            return 'DANGEROUS'
        elif temperature >= 33:
            return 'HIGH'
        elif temperature >= 27:
            return 'MODERATE'
        else:
            return 'NORMAL'
    
    def get_risk_description(self, risk_level):
        """Get description and color for each risk level"""
        risk_info = {
            'DANGEROUS': {
                'description': 'High risk of serious heat illness. Avoid exertion, cool down immediately, and seek medical help for severe symptoms.',
                'color': '#ef4444',
                'badge_class': 'danger'
            },
            'HIGH': {
                'description': 'Heat exhaustion may occur. Limit outdoor activity, rest in shade, and hydrate often.',
                'color': '#f97316',
                'badge_class': 'warning'
            },
            'MODERATE': {
                'description': 'Mild heat stress possible. Drink water and reduce prolonged sun exposure.',
                'color': '#f59e0b',
                'badge_class': 'warning'
            },
            'NORMAL': {
                'description': 'Minimal heat risk. Stay hydrated.',
                'color': '#10b981',
                'badge_class': 'success'
            },
            'UNKNOWN': {
                'description': 'Data unavailable',
                'color': '#6b7280',
                'badge_class': 'secondary'
            }
        }
        return risk_info.get(risk_level, risk_info['UNKNOWN'])
    
    def should_trigger_alert(self, risk_level):
        """Determine if alert should be sent based on risk level"""
        return risk_level in ['HIGH', 'DANGEROUS']
    
    def generate_alert_message(self, location_name, temperature, humidity, risk_level, heat_index):
        """Generate alert message for email"""
        risk_info = self.get_risk_description(risk_level)
        
        # Temperature range info
        temp_ranges = {
            'NORMAL': 'below 27°C',
            'MODERATE': '27–32°C',
            'HIGH': '33–41°C',
            'DANGEROUS': '42°C and above'
        }
        
        message = f"""
        🔥 HEATWATCH ALERT - {risk_level} HEAT RISK 🔥
        
        Location: {location_name}
        Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        
        Current Conditions:
        - Temperature: {temperature}°C (Range: {temp_ranges.get(risk_level, 'Unknown')})
        - Humidity: {humidity}%
        - Heat Index: {heat_index}°C
        - Risk Level: {risk_level}
        
        Advisory: {risk_info['description']}
        
        Please take necessary precautions based on risk level.
        
        --
        HeatWatch: Machine Learning GIS-Based Heat Risk Monitoring System
        Auto-generated alert - Please do not reply
        """
        return message