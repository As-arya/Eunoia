"""
Euonia Flask Application
"""
from flask import Flask, jsonify, request
from app.config import Config
from app.extensions import db, jwt, cors


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    app.url_map.strict_slashes = False
    
    # Init extensions
    db.init_app(app)
    jwt.init_app(app)
    # CORS configuration - allow Vercel and localhost
    cors.init_app(app, resources={
        r"/api/*": {
            "origins": ["http://localhost:5173", "http://localhost:3000", "https://*.vercel.app"],
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization"],
            "supports_credentials": True
        }
    })
    
    # Also handle CORS for all origins in production (backup)
    @app.after_request
    def after_request(response):
        origin = request.headers.get('Origin')
        if origin:
            response.headers['Access-Control-Allow-Origin'] = origin
            response.headers['Access-Control-Allow-Credentials'] = 'true'
            response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'
            response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
        return response
    
    # JWT handlers
    @jwt.invalid_token_loader
    def invalid_token(error):
        print(f"[JWT] Invalid token error: {error}")
        return jsonify({'error': 'Invalid token', 'reason': error}), 401
    
    @jwt.unauthorized_loader
    def unauthorized(error):
        return jsonify({'error': 'Missing token'}), 401
    
    @jwt.expired_token_loader
    def expired_token(header, payload):
        return jsonify({'error': 'Token expired'}), 401
    
    # Register routes
    from app.routes import auth_bp, users_bp, sessions_bp, screening_bp, insights_bp
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(users_bp, url_prefix='/api/users')
    app.register_blueprint(sessions_bp, url_prefix='/api/sessions')
    app.register_blueprint(screening_bp, url_prefix='/api/screening')
    app.register_blueprint(insights_bp, url_prefix='/api/insights')
    
    # Health check
    @app.route('/api/health')
    def health():
        return jsonify({'status': 'healthy'})
    
    # Create tables
    with app.app_context():
        db.create_all()
        from app.seeds.questions import seed_questions, update_religious_text
        seed_questions()
        update_religious_text()  # Update any religious text to neutral alternatives
    
    return app
