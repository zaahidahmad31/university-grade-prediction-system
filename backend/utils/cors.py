from flask_cors import CORS

def configure_cors(app):
    """Configure CORS for the application"""
    origins = app.config.get('CORS_ORIGINS', '*')
    
    # If origins is a string, convert to list
    if isinstance(origins, str) and origins != '*':
        origins = [origin.strip() for origin in origins.split(',')]
    
    # Configure CORS
    CORS(app, resources={
        r"/api/*": {
            "origins": origins,
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization"]
        }
    })
    
    app.logger.info(f"CORS configured with origins: {origins}")
    
    return app