import numpy as np
import joblib
import os
from datetime import datetime

class HeatRiskMLModel:
    def __init__(self, model_name='rf'):
        self.model = None
        self.scaler = None
        self.model_name = model_name
        self.is_trained = False
        
        # Model paths for FORECASTING models
        base_path = os.path.join(os.path.dirname(__file__), '..', 'instance')
        self.model_paths = {
            'rf': os.path.join(base_path, 'random_forest_forecast.pkl'),
            'dt': os.path.join(base_path, 'decision_tree_forecast.pkl'),
            'knn': os.path.join(base_path, 'k_nearest_neighbors_forecast.pkl')
        }
        self.scaler_path = os.path.join(base_path, 'scaler_forecast.pkl')
        
        # Model display names
        self.model_names = {
            'rf': 'Random Forest',
            'dt': 'Decision Tree',
            'knn': 'K-Nearest Neighbors'
        }
        
        # Model R² scores (from training)
        self.model_r2 = {
            'rf': 0.9555,
            'dt': 0.9329,
            'knn': 0.9193
        }
        
        # Model MAE scores
        self.model_mae = {
            'rf': 0.58,
            'dt': 0.73,
            'knn': 0.73
        }
        
        # Load model
        self.load_model(model_name)
    
    def switch_model(self, model_name):
        """Switch to a different ML model"""
        if model_name in self.model_paths:
            self.load_model(model_name)
            return True
        return False
    
    def get_available_models(self):
        """Get list of available models"""
        available = []
        for key, path in self.model_paths.items():
            if os.path.exists(path):
                available.append({
                    'id': key,
                    'name': self.model_names.get(key, key),
                    'r2': self.model_r2.get(key, 0),
                    'mae': self.model_mae.get(key, 0),
                    'loaded': key == self.model_name
                })
        return available
    
    def predict_temperature(self, temperature, humidity, heat_index=None):
        """Predict temperature 6 hours ahead and classify risk"""
        if not self.is_trained or self.model is None:
            return None, None
        
        if heat_index is None:
            heat_index = temperature + 0.05 * humidity
        
        now = datetime.now()
        hour = now.hour
        month = now.month
        day = now.day
        
        features = np.array([[temperature, humidity, heat_index, hour, month, day]])
        features_scaled = self.scaler.transform(features)
        
        predicted_temp = self.model.predict(features_scaled)[0]
        predicted_temp = round(float(predicted_temp), 1)
        
        # Classify predicted temperature into risk level
        if predicted_temp >= 42:
            predicted_risk = 'DANGEROUS'
        elif predicted_temp >= 33:
            predicted_risk = 'HIGH'
        elif predicted_temp >= 27:
            predicted_risk = 'MODERATE'
        else:
            predicted_risk = 'NORMAL'
        
        return predicted_temp, predicted_risk
    
    def load_model(self, model_name):
        """Load trained model from disk"""
        try:
            model_path = self.model_paths.get(model_name)
            if model_path and os.path.exists(model_path) and os.path.exists(self.scaler_path):
                self.model = joblib.load(model_path)
                self.scaler = joblib.load(self.scaler_path)
                self.model_name = model_name
                self.is_trained = True
                print(f"📂 Forecast Model loaded: {self.model_names.get(model_name, model_name)}")
                return True
        except Exception as e:
            print(f"⚠️  Could not load model '{model_name}': {e}")
        
        self.is_trained = False
        return False
    
    def get_model_info(self):
        """Get model information"""
        available = self.get_available_models()
        
        return {
            'status': 'Loaded' if self.is_trained else 'Not loaded',
            'current_model': self.model_names.get(self.model_name, 'None'),
            'type': 'Temperature Forecast (6h ahead)',
            'r2_score': self.model_r2.get(self.model_name, 0),
            'mae': self.model_mae.get(self.model_name, 0),
            'available_models': available,
            'features': ['Temperature', 'Humidity', 'Heat Index', 'Hour', 'Month', 'Day']
        }