import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from flask import current_app
from datetime import datetime, timedelta

# Email Configuration
ADMIN_EMAIL = "aztechworx@gmail.com"
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SENDER_EMAIL = "aztechworx@gmail.com"
SENDER_PASSWORD = "auahlcddwxcjwf"

# Track last email sent per location to prevent spam
_last_email_sent = {}  # {location_name: datetime}

class EmailService:
    def __init__(self, app=None):
        self.app = app
        self.cooldown_hours = 1  # Only send email once per hour per location
    
    def can_send_email(self, location_name):
        """Check if enough time has passed since last email for this location"""
        if location_name not in _last_email_sent:
            return True
        
        time_since_last = datetime.now() - _last_email_sent[location_name]
        return time_since_last.total_seconds() >= (self.cooldown_hours * 3600)
    
    def send_alert_email(self, recipient, subject, message_body):
        """Send alert email using SMTP"""
        try:
            # Create message
            msg = MIMEMultipart()
            msg['From'] = SENDER_EMAIL
            msg['To'] = recipient
            msg['Subject'] = subject
            
            msg.attach(MIMEText(message_body, 'plain'))
            
            # Send email
            with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
                server.starttls()
                server.login(SENDER_EMAIL, SENDER_PASSWORD)
                server.send_message(msg)
            
            print(f"✓ Alert email sent to {recipient}")
            return True
            
        except Exception as e:
            print(f"✗ Error sending email: {e}")
            return False
    
    def check_and_send_heat_alert(self, location_name, temperature, humidity, risk_level, heat_index, recipient=None):
        """Check risk level and send alert if HIGH or DANGEROUS (with cooldown)"""
        if recipient is None:
            recipient = ADMIN_EMAIL
        
        if risk_level not in ['HIGH', 'DANGEROUS']:
            return False
        
        # Check cooldown - only send once per hour per location
        if not self.can_send_email(location_name):
            time_since = datetime.now() - _last_email_sent.get(location_name, datetime.now())
            minutes_left = 60 - (time_since.total_seconds() / 60)
            print(f"⏰ Cooldown active for {location_name}. Next email in {int(minutes_left)} minutes.")
            return False
        
        subject = f"🔥 HEATWATCH ALERT: {risk_level} Heat Risk in {location_name}"
        
        advisories = {
            'NORMAL': 'Minimal heat risk. Stay hydrated.',
            'MODERATE': 'Mild heat stress possible. Drink water and reduce prolonged sun exposure.',
            'HIGH': 'Heat exhaustion may occur. Limit outdoor activity, rest in shade, and hydrate often.',
            'DANGEROUS': 'High risk of serious heat illness. Avoid exertion, cool down immediately, and seek medical help for severe symptoms.'
        }
        advisory = advisories.get(risk_level, 'Please take necessary precautions.')
        
        message = f"""
HEATWATCH HEAT RISK ALERT
══════════════════════════════

Location: {location_name}
Risk Level: {risk_level}
Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

Current Conditions:
    🌡️  Temperature: {temperature}°C
    💧 Humidity: {humidity}%
    🔥 Heat Index: {heat_index}°C

⚠️  ADVISORY: {advisory}

Please take necessary precautions:
    • Stay hydrated and drink plenty of water
    • Avoid prolonged sun exposure
    • Wear light, loose-fitting clothing
    • Check on vulnerable family members and neighbors

══════════════════════════════
HeatWatch: ML GIS-Based Heat Risk Monitoring System
Auto-generated alert - Next alert for this location in {self.cooldown_hours} hour(s)
        """
        
        if self.send_alert_email(recipient, subject, message):
            _last_email_sent[location_name] = datetime.now()
            return True
        
        return False
    
    def send_custom_alert(self, recipient, location_name, temperature, humidity, risk_level, heat_index, predicted_temp=None, predicted_risk=None):
        """Send alert to custom email address with ML forecast"""
        subject = f"🔥 HEATWATCH ALERT: {risk_level} Heat Risk in {location_name}"
        
        advisories = {
            'NORMAL': 'Minimal heat risk. Stay hydrated.',
            'MODERATE': 'Mild heat stress possible. Drink water and reduce prolonged sun exposure.',
            'HIGH': 'Heat exhaustion may occur. Limit outdoor activity, rest in shade, and hydrate often.',
            'DANGEROUS': 'High risk of serious heat illness. Avoid exertion, cool down immediately, and seek medical help for severe symptoms.'
        }
        advisory = advisories.get(risk_level, 'Please take necessary precautions.')
        
        # Forecast section
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

Current Conditions:
    🌡️  Temperature: {temperature}°C
    💧 Humidity: {humidity}%
    🔥 Heat Index: {heat_index}°C

⚠️  ADVISORY: {advisory}
{forecast_section}
🤖 Powered by HeatWatch ML Temperature Forecast Model

This alert was sent from HeatWatch System.
══════════════════════════════
HeatWatch: ML GIS-Based Heat Risk Monitoring System
Built by Engr. Brian Ezekiel D. Batalon, ECE, ECT, SO2
        """
        
        return self.send_alert_email(recipient, subject, message)