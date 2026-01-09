"""Euonia API Server"""
from app import create_app
from app.services.gemini_service import configure_gemini

configure_gemini()
app = create_app()

if __name__ == '__main__':
    print("=" * 40)
    print("🌿 Euonia API Server")
    print("http://localhost:5000")
    print("=" * 40)
    app.run(host='0.0.0.0', port=5000, debug=True)
