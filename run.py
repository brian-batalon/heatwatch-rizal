"""
HeatWatch Rizal - Heat Risk Monitoring System
Entry point for running the Flask application
"""

from app import create_app

app = create_app()

if __name__ == '__main__':
    print("=" * 50)
    print("🔥 HeatWatch Rizal - Heat Risk Monitoring System")
    print("=" * 50)
    print("Starting Flask development server...")
    print("Access the application at: http://127.0.0.1:5000")
    print("Press Ctrl+C to stop the server")
    print("=" * 50)
    
    app.run(debug=False, host='127.0.0.1', port=5000)