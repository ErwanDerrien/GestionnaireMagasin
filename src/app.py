from flask import Flask, jsonify, request
from sqlalchemy.exc import SQLAlchemyError
from flasgger import Swagger
from prometheus_flask_exporter import PrometheusMetrics
from prometheus_client import generate_latest
from datetime import timedelta
from src.security import cors_response

from config.variables import HOST, APP_PORT, API_MASK, VERSION, REDIS_PORT
from src.utils.extensions import cache

app = Flask(__name__)

# Config Swagger
swagger = Swagger(app)

# Config Redis Cache
app.config['CACHE_TYPE'] = 'RedisCache'
app.config['CACHE_REDIS_HOST'] = 'redis'
app.config['CACHE_REDIS_PORT'] = REDIS_PORT
app.config['CACHE_REDIS_DB'] = 0
app.config['CACHE_REDIS_PASSWORD'] = None
app.config['CACHE_DEFAULT_TIMEOUT'] = 300
cache.init_app(app)
import os
instance_num = os.getenv('INSTANCE_NUM', 'standalone')

# Config routes blueprints
from src.controllers.auth_controller import auth_bp
from src.controllers.product_controller import product_bp
from src.controllers.order_controller import order_bp
from src.controllers.admin_controller import admin_bp
app.register_blueprint(auth_bp, url_prefix=f'/{API_MASK}/{VERSION}/auth')
app.register_blueprint(product_bp, url_prefix=f'/{API_MASK}/{VERSION}/products')
app.register_blueprint(order_bp, url_prefix=f'/{API_MASK}/{VERSION}/orders')
app.register_blueprint(admin_bp)

# Config
app.config['SECRET_KEY'] = 'votre_cle_secrete_complexe'
app.config['JWT_EXPIRATION_DELTA'] = timedelta(hours=1)
app.config['SWAGGER'] = {
    'title': 'Store Manager API',
    'version': f'{VERSION}',
    'description': 'API pour la gestion de magasins et produits',
    'specs_route': '/apidocs/'
}

# Config Prometheus
metrics = PrometheusMetrics(app)
@app.route('/metrics')
def custom_metrics():
    from flask import Response
    data = generate_latest()
    response = Response(data, mimetype='text/plain')
    return cors_response(response, 200)

@app.route(f'/{API_MASK}/{VERSION}/')
def home():
    return {"message": "API fonctionnelle"}
  
if __name__ == '__main__':
    app.run(host="0.0.0.0", port=APP_PORT, debug=True)