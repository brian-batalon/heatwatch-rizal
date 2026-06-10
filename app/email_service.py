import requests
import os
from flask import current_app
from datetime import datetime, timedelta

# SendGrid Configuration
SENDGRID_API_KEY = os.environ.get('SENDGRID_API_KEY', '')
SENDER_EMAIL = "aztechworx@gmail.com"
ADMIN_EMAIL = "aztechworx@gmail.com"

# Track last email sent per location to prevent spam
_last_email_sent = {}

class EmailService:
    def __init__(self, app=None):
        self.app = app
        self.cooldown_hours = 1
    
    def can_send_email(self, location_name):
        if location_name not in _last_email_sent:
            return True
        time_since_last = datetime.now() - _last_email_sent[location_name]
        return time_since_last.total_seconds() >= (self.cooldown_hours * 3600)
    
    def send_alert_email(self, recipient, subject, message_body):
        try:
            url = "https://api.sendgrid.com/v3/mail/send"
            headers = {
                "Authorization": f"Bearer {SENDGRID_API_KEY}",
                "Content-Type": "application/json"
            }
            data = {
                "personalizations": [{"to": [{"email": recipient}]}],
                "from": {"email": SENDER_EMAIL, "name": "HeatWatch Rizal"},
                "subject": subject,
                "content": [{"type": "text/plain", "value": message_body}]
            }
            response = requests.post(url, headers=headers, json=data, timeout=10)
            if response.status_code == 202:
                print(f"✓ Alert email sent to {recipient}")
                return True
            else:
                print(f"✗ SendGrid error: {response.status_code} - {response.text}")
                return False
        except Exception as e:
            print(f"✗ Error sending email: {e}")
            return False
    
    def send_custom_alert(self, recipient, location_name, temperature, humidity, risk_level, heat_index, predicted_temp=None, predicted_risk=None):
        subject = f"🔥 HEATWATCH ALERT: {risk_level} Heat Risk in {location_name}"
        advisories = {
            'NORMAL': 'Minimal heat risk. Stay hydrated.',
            'MODERATE': 'Mild heat stress possible. Drink water and reduce prolonged sun exposure.',
            'HIGH': 'Heat exhaustion may occur. Limit outdoor activity, rest in shade, and hydrate often.',
            'DANGEROUS': 'High risk of serious heat illness. Avoid exertion, cool down immediately, and seek medical help for severe symptoms.'
        }
        advisory = advisories.get(risk_level, 'Please take necessary precautions.')
        forecast_section = ""
        if predicted_temp is not None and predicted_risk is not None:
            forecast_section = f"""
📈 6-HOUR ML FORECAST:
    🌡️  Predicted Temperature: {predicted_temp}°C
    ⚠️  Predicted Risk Level: {predicted_risk}
"""
        message = f"""
HEATWATCH HEAT RISK ALERT
══════════════════════════════
Location: {location_name}
Risk Level: {risk_level}
Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
🌡️  Temperature: {temperature}°C | 💧 Humidity: {humidity}% | 🔥 Heat Index: {heat_index}°C
⚠️  ADVISORY: {advisory}{forecast_section}
🤖 Powered by HeatWatch ML Temperature Forecast Model
══════════════════════════════
HeatWatch: ML GIS-Based Heat Risk Monitoring System
Built by Engr. Brian Ezekiel D. Batalon, ECE, ECT, SO2
        """
        return self.send_alert_email(recipient, subject, message)