from flask import Flask, Response
from flasgger import Swagger
from prometheus_flask_exporter import PrometheusMetrics
from datetime import timedelta
import os

from config.variables import HOST, APP_PORT, API_MASK, VERSION, REDIS_PORT
from src.utils.extensions import cache
from src.security import cors_response

def create_app():
    app = Flask(__name__)
    
    # Configuration de base
    _configure_app(app)
    
    # Initialisation des extensions
    _initialize_extensions(app)
    
    # Enregistrement des blueprints
    _register_blueprints(app)
    
    # Routes spéciales
    _add_special_routes(app)
    
    return app

def _configure_app(app):
    """Configure les paramètres de l'application"""
    app.config.update({
        # Sécurité
        'SECRET_KEY': os.getenv('SECRET_KEY', 'votre_cle_secrete_complexe'),
        'JWT_EXPIRATION_DELTA': timedelta(hours=1),
        
        # Cache Redis
        'CACHE_TYPE': 'RedisCache',
        'CACHE_REDIS_HOST': 'redis',
        'CACHE_REDIS_PORT': REDIS_PORT,
        'CACHE_REDIS_DB': 0,
        'CACHE_REDIS_PASSWORD': None,
        'CACHE_DEFAULT_TIMEOUT': 300,
        
        # Swagger
        'SWAGGER': {
            'title': 'Store Manager API',
            'version': VERSION,
            'description': 'API pour la gestion de magasins et produits',
            'specs_route': '/apidocs/'
        }
    })

def _initialize_extensions(app):
    """Initialise les extensions Flask"""
    # Swagger
    Swagger(app)
    
    # Cache
    cache.init_app(app)
    
    # Prometheus
    metrics = PrometheusMetrics(app)
    metrics.info('app_info', 'Application info', version=VERSION)

def _register_blueprints(app):
    """Enregistre les blueprints"""
    from src.controllers.auth_controller import auth_bp
    from src.controllers.product_controller import product_bp
    from src.controllers.order_controller import order_bp
    from src.controllers.admin_controller import admin_bp
    
    app.register_blueprint(auth_bp, url_prefix=f'/{API_MASK}/{VERSION}/auth')
    app.register_blueprint(product_bp, url_prefix=f'/{API_MASK}/{VERSION}/products')
    app.register_blueprint(order_bp, url_prefix=f'/{API_MASK}/{VERSION}/orders')
    app.register_blueprint(admin_bp)

def _add_special_routes(app):
    """Ajoute les routes spéciales"""
    @app.route('/metrics')
    def metrics():
        from prometheus_client import generate_latest
        data = generate_latest()
        return cors_response(Response(data, mimetype='text/plain'), 200)
    
    @app.route(f'/{API_MASK}/{VERSION}/')
    def home():
        return {"message": "API fonctionnelle"}

app = create_app()

if __name__ == '__main__':
    app.run(host=os.getenv('HOST', '0.0.0.0'), 
            port=int(os.getenv('PORT', APP_PORT)),
            debug=os.getenv('DEBUG', 'False').lower() == 'true')