from flask import Flask, jsonify, request
from sqlalchemy.exc import SQLAlchemyError
from flasgger import Swagger, swag_from
from prometheus_flask_exporter import PrometheusMetrics
from prometheus_client import generate_latest, PROCESS_COLLECTOR
from flask_caching import Cache
from datetime import timedelta
from data.database import reset_database
from src.services.product_services import restock_store_products, search_product_service, stock_status
from src.services.order_services import orders_status, save_order, return_order, generate_orders_report
from src.services.login_services import login
from src.security import generate_jwt, role_required, build_error_response, build_cors_preflight_response, cors_response
import json
import hashlib
import redis

from flask import Flask, jsonify
from prometheus_flask_exporter import PrometheusMetrics
from src.security import cors_response

app = Flask(__name__)

# Add other routes blueprints
from src.controllers.auth_controller import auth_bp
app.register_blueprint(auth_bp, url_prefix='/api/v2/auth')

# Configuration
app.config['SECRET_KEY'] = 'votre_cle_secrete_complexe'
app.config['JWT_EXPIRATION_DELTA'] = timedelta(hours=1)
app.config['SWAGGER'] = {
    'title': 'Store Manager API',
    'version': '1.0',
    'description': 'API pour la gestion de magasins et produits',
    'specs_route': '/apidocs/'
}

# Configuration Redis Cache
app.config['CACHE_TYPE'] = 'RedisCache'
app.config['CACHE_REDIS_HOST'] = 'redis'
app.config['CACHE_REDIS_PORT'] = 6379
app.config['CACHE_REDIS_DB'] = 0
app.config['CACHE_REDIS_PASSWORD'] = None  # Ajoutez votre mot de passe Redis si nécessaire
app.config['CACHE_DEFAULT_TIMEOUT'] = 300  # 5 minutes par défaut

# Initialisation du cache
cache = Cache(app)

swagger = Swagger(app)

def generate_cache_key(prefix, **kwargs):
    """Génère une clé de cache unique basée sur les paramètres"""
    key_data = json.dumps(kwargs, sort_keys=True)
    key_hash = hashlib.md5(key_data.encode()).hexdigest()
    return f"{prefix}:{key_hash}"

def invalidate_cache_pattern(pattern):
    """Invalide les clés de cache correspondant à un pattern"""
    try:
        redis_client = redis.Redis(
            host=app.config['CACHE_REDIS_HOST'],
            port=app.config['CACHE_REDIS_PORT'],
            db=app.config['CACHE_REDIS_DB'],
            password=app.config['CACHE_REDIS_PASSWORD']
        )
        keys = list(redis_client.scan_iter(pattern))
        if keys:
            redis_client.delete(*keys)
            print(f"Cache invalidé pour le pattern: {pattern}, {len(keys)} clés supprimées")
    except Exception as e:
        print(f"Erreur lors de l'invalidation du cache: {str(e)}")
        
# Prometheus config
# PROCESS_COLLECTOR.register()
metrics = PrometheusMetrics(app, path='/test')
@app.route('/metrics')
def custom_metrics():
    from flask import Response
    data = generate_latest()
    response = Response(data, mimetype='text/plain')
    return cors_response(response, 200)

import os

instance_num = os.getenv('INSTANCE_NUM', 'standalone')

@app.route('/instance-info')
def instance_info():
    if request.method == "OPTIONS":
        return build_cors_preflight_response()
        
    try:
        data = request.get_json()
        if not data:
            return cors_response(build_error_response(400, "Bad Request", "Aucune donnée fournie", request.path), 400)

        username = data.get("username")
        password = data.get("password")
        store_id = data.get("store_id")

        if not username or not password:
            return cors_response(build_error_response(400, "Bad Request", "Identifiants manquants", request.path), 400)

        result = login(username, password, store_id)
        
        if result and result.get("success"):
            token = generate_jwt(
                user_id=result.get("user_id"),
                username=username,
                role=result.get("role"),
                store_id=store_id
            )
            return cors_response({
                "status": "success",
                "token": token,
                "user": {
                    "username": username,
                    "role": result.get("role"),
                    "store_id": store_id
                }
            }, 200)
        else:
            status_code = result.get("status_code", 401) if result else 401
            message = result.get("error", "Identifiants incorrects") if result else "Échec de l'authentification"
            return cors_response(
                build_error_response(status_code, "Unauthorized", message, request.path),
                status_code
            )

    except Exception as e:
        return cors_response(
            build_error_response(500, "Internal Server Error", f"Erreur: {str(e)}", request.path),
            500
        )

@app.route("/api/v2/")
def home():
    return {"message": "API fonctionnelle"}

@app.route("/api/v2/products", methods=["GET", "OPTIONS"])
@role_required('get_all_products')
@swag_from({
    'tags': ['Produits'],
    'description': 'Récupère tous les produits avec pagination',
    'parameters': [
        {
            'name': 'page',
            'in': 'query',
            'type': 'integer',
            'required': False,
            'default': 1,
            'description': 'Numéro de page'
        },
        {
            'name': 'per_page',
            'in': 'query',
            'type': 'integer',
            'required': False,
            'default': 10,
            'description': 'Nombre d\'éléments par page'
        }
    ],
    'responses': {
        200: {
            'description': 'Liste paginée des produits',
            'schema': {
                'type': 'object',
                'properties': {
                    'status': {'type': 'string'},
                    'data': {
                        'type': 'array',
                        'items': {
                            'type': 'object',
                            'properties': {
                                'id': {'type': 'integer'},
                                'name': {'type': 'string'},
                                'category': {'type': 'string'},
                                'price': {'type': 'number'},
                                'stock_quantity': {'type': 'integer'},
                                'store_id': {'type': 'integer'}
                            }
                        }
                    },
                    'pagination': {
                        'type': 'object',
                        'properties': {
                            'total': {'type': 'integer'},
                            'pages': {'type': 'integer'},
                            'page': {'type': 'integer'},
                            'per_page': {'type': 'integer'},
                            'next': {'type': 'string', 'nullable': True},
                            'prev': {'type': 'string', 'nullable': True}
                        }
                    }
                }
            }
        },
        401: {'description': 'Non autorisé'},
        403: {'description': 'Permission refusée'},
        500: {'description': 'Erreur serveur'}
    }
})
def get_all_products_route():
    if request.method == "OPTIONS":
        return build_cors_preflight_response()
        
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        
        # Générer la clé de cache
        cache_key = generate_cache_key("all_products", page=page, per_page=per_page)
        
        # Vérifier le cache
        cached_result = cache.get(cache_key)
        if cached_result:
            return cors_response(jsonify(cached_result), 200)
        
        products_data, pagination = stock_status(page=page, per_page=per_page)
        
        response_data = {
            "status": "success",
            "data": products_data,
            "pagination": pagination
        }
        
        # Mettre en cache (5 minutes)
        cache.set(cache_key, response_data, timeout=300)
        
        return cors_response(response_data, 200)

    except Exception as e:
        error = build_error_response(
            500,
            "Internal Server Error",
            f"Erreur lors de la récupération du stock: {str(e)}",
            request.path
        )
        return cors_response(error, 500)
        
@app.route("/api/v2/products/<int:store_id>", methods=["GET", "OPTIONS"])
@role_required('get_all_products_of_store')
@swag_from({
    'tags': ['Produits'],
    'description': 'Récupère les produits d\'un magasin spécifique',
    'parameters': [
        {
            'name': 'store_id',
            'in': 'path',
            'type': 'integer',
            'required': True,
            'description': 'ID du magasin'
        }
    ],
    'responses': {
        200: {'description': 'Liste des produits du magasin'},
        401: {'description': 'Non autorisé'},
        403: {'description': 'Permission refusée'},
        404: {'description': 'Magasin non trouvé'},
        500: {'description': 'Erreur serveur'}
    }
})
def get_all_products_of_store_route(store_id):
    if request.method == "OPTIONS":
        return build_cors_preflight_response()
        
    try:
        cache_key = generate_cache_key(f"store_products_{store_id}")
        cached = cache.get(cache_key)
        if cached:
            return cors_response(jsonify(cached), 200)

        products_data = stock_status(store_id)
        if not products_data:
            error = build_error_response(
                404,
                "Not Found",
                f"Aucun produit trouvé pour le magasin {store_id}",
                request.path
            )
            return cors_response(error, 404)

        response_data = {
            "status": "success",
            "data": products_data,
            "count": len(products_data)
        }
        cache.set(cache_key, response_data, timeout=300)
        return cors_response(jsonify(response_data), 200)

    except Exception as e:
        error = build_error_response(
            500,
            "Internal Server Error",
            f"Erreur lors de la récupération du stock: {str(e)}",
            request.path
        )
        return cors_response(error, 500)

@app.route("/api/v2/products/<int:store_id>/<search_term>", methods=["GET", "OPTIONS"])
@role_required('search_product')
@swag_from({
    'tags': ['Produits'],
    'description': 'Recherche de produits par magasin',
    'parameters': [
        {
            'name': 'store_id',
            'in': 'path',
            'type': 'integer',
            'required': True,
            'description': 'ID du magasin'
        },
        {
            'name': 'search_term',
            'in': 'path',
            'type': 'string',
            'required': True,
            'description': 'Terme de recherche (nom, catégorie ou ID du produit)'
        },
        {
            'name': 'page',
            'in': 'query',
            'type': 'integer',
            'required': False,
            'default': 1,
            'description': 'Numéro de page'
        },
        {
            'name': 'per_page',
            'in': 'query',
            'type': 'integer',
            'required': False,
            'default': 10,
            'description': 'Nombre d\'éléments par page'
        }
    ],
    'responses': {
        200: {'description': 'Résultats de la recherche avec pagination'},
        400: {'description': 'Paramètres invalides'},
        401: {'description': 'Non autorisé'},
        403: {'description': 'Permission refusée'},
        500: {'description': 'Erreur serveur'}
    }
})
def search_product_route(store_id, search_term):
    if request.method == "OPTIONS":
        return build_cors_preflight_response()
        
    try:
        if not search_term or len(search_term) < 2:
            error = build_error_response(
                400,
                "Bad Request",
                "Le terme de recherche doit contenir au moins 2 caractères",
                request.path
            )
            return cors_response(error, 400)

        # Récupération des paramètres de pagination
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        
        # Validation des paramètres de pagination
        if page < 1:
            page = 1
        if per_page < 1 or per_page > 100:  # Limite maximale pour éviter les surcharges
            per_page = 10

        # Générer la clé de cache
        cache_key = generate_cache_key("product_search", store_id=store_id, search_term=search_term, page=page, per_page=per_page)
        
        # Vérifier le cache
        cached_result = cache.get(cache_key)
        if cached_result:
            return cors_response(jsonify(cached_result), 200)

        products, pagination_info = search_product_service(search_term, store_id, page, per_page)
        
        response_data = {
            "status": "success",
            "data": products,
            "pagination": pagination_info,
            "message": "Aucun produit trouvé" if not products else None
        }
        
        # Mettre en cache (2 minutes)
        cache.set(cache_key, response_data, timeout=120)
        
        return cors_response(response_data, 200)
    
    except Exception as e:
        error = build_error_response(
            500,
            "Internal Server Error",
            f"Erreur lors de la recherche: {str(e)}",
            request.path
        )
        return cors_response(error, 500)

@app.route("/api/v2/orders", methods=["POST", "OPTIONS"])
@role_required('save_order')
@swag_from({
    'tags': ['Commandes'],
    'description': 'Créer une nouvelle commande',
    'parameters': [
        {
            'name': 'body',
            'in': 'body',
            'required': True,
            'schema': {
                'type': 'object',
                'properties': {
                    'store_id': {'type': 'integer'},
                    'products': {
                        'type': 'array',
                        'items': {
                            'product_id': {'type': 'integer'},
                            'quantity': {'type': 'integer'}
                        }
                    }
                }
            }
        }
    ],
    'responses': {
        201: {'description': 'Commande créée'},
        400: {'description': 'Données invalides'},
        401: {'description': 'Non autorisé'},
        403: {'description': 'Permission refusée'},
        404: {'description': 'Produit non trouvé'},
        409: {'description': 'Stock insuffisant'},
        500: {'description': 'Erreur serveur'}
    }
})
def create_order_route():
    if request.method == "OPTIONS":
        return build_cors_preflight_response()

    try:
        data = request.get_json()

        if not data:
            error = build_error_response(
                400,
                "Bad Request",
                "Aucune donnée reçue",
                request.path
            )
            return cors_response(error, 400)

        if 'store_id' not in data:
            error = build_error_response(
                400,
                "Bad Request",
                "Le champ 'store_id' est obligatoire",
                request.path
            )
            return cors_response(error, 400)

        result = save_order(data)

        if result.get("status") == "success":
            # Invalider le cache des commandes et produits
            invalidate_cache_pattern("all_orders:*")
            invalidate_cache_pattern("all_products:*")
            invalidate_cache_pattern(f"store_products_{data['store_id']}:*")
            
            return cors_response({  
                "status": "success",
                "message": result.get("message", "Commande enregistrée"),
                "order": {
                    "id": result.get("order_id"),
                    "total": result.get("total"),
                    "products": result.get("products"),
                    "store_id": result.get("store_id")
                }
            }, 201)

        elif result.get("status") == "error":
            message = result.get("message", "Erreur lors de la commande")
            errors = result.get("errors", [])
            
            error_type = "Bad Request"
            status_code = 400
            
            if any("stock insuffisant" in err.lower() for err in errors):
                error_type = "Conflict"
                status_code = 409
            elif any("non trouvé" in err.lower() for err in errors):
                error_type = "Not Found"
                status_code = 404
                
            error = build_error_response(
                status_code,
                error_type,
                message,
                request.path
            )
            error["errors"] = errors
            error["store_id"] = result.get("store_id")
            
            return cors_response(error, status_code)

        error = build_error_response(
            500,
            "Internal Server Error",
            "Réponse du service inattendue",
            request.path
        )
        return cors_response(error, 500)

    except Exception as e:
        error = build_error_response(
            500,
            "Internal Server Error",
            f"Erreur serveur: {str(e)}",
            request.path
        )
        return cors_response(error, 500)

@app.route("/api/v2/orders/<int:order_id>", methods=["PUT", "OPTIONS"])
@role_required('return_order')
@swag_from({
    'tags': ['Commandes'],
    'description': 'Retourner une commande',
    'parameters': [
        {
            'name': 'order_id',
            'in': 'path',
            'type': 'integer',
            'required': True
        }
    ],
    'responses': {
        200: {'description': 'Commande retournée'},
        400: {'description': 'Erreur dans la requête'},
        401: {'description': 'Non autorisé'},
        403: {'description': 'Permission refusée'},
        404: {'description': 'Commande non trouvée'},
        500: {'description': 'Erreur serveur'}
    }
})
def return_order_route(order_id):
    if request.method == "OPTIONS":
        return build_cors_preflight_response()

    try:
        result = return_order(order_id)

        if "erreur" in result.lower() or "non trouvée" in result.lower():
            status_code = 404 if "non trouvée" in result.lower() else 400
            error_type = "Not Found" if status_code == 404 else "Bad Request"
            
            error = build_error_response(
                status_code,
                error_type,
                result,
                request.path
            )
            return cors_response(error, status_code)

        # Invalider le cache après retour de commande
        invalidate_cache_pattern("all_orders:*")
        invalidate_cache_pattern("all_products:*")

        return cors_response({
            "status": "success",
            "message": result,
            "order_id": order_id
        }, 200)

    except Exception as e:
        error = build_error_response(
            500,
            "Internal Server Error",
            f"Erreur serveur: {str(e)}",
            request.path
        )
        return cors_response(error, 500)

@app.route("/api/v2/orders", methods=["GET", "OPTIONS"])
@role_required('get_all_orders')
@swag_from({
    'tags': ['Commandes'],
    'description': 'Récupère toutes les commandes avec pagination',
    'parameters': [
        {
            'name': 'page',
            'in': 'query',
            'type': 'integer',
            'required': False,
            'default': 1,
            'description': 'Numéro de page'
        },
        {
            'name': 'per_page',
            'in': 'query',
            'type': 'integer',
            'required': False,
            'default': 10,
            'description': 'Nombre d\'éléments par page'
        }
    ],
    'responses': {
        200: {
            'description': 'Liste paginée des commandes',
            'schema': {
                'type': 'object',
                'properties': {
                    'status': {'type': 'string'},
                    'data': {
                        'type': 'array',
                        'items': {
                            'type': 'object',
                            'properties': {
                                'id': {'type': 'integer'},
                                'user_id': {'type': 'string'},
                                'status': {'type': 'string'},
                                'products': {
                                    'type': 'array',
                                    'items': {'type': 'integer'}
                                },
                                'total_price': {'type': 'number'},
                                'store_id': {'type': 'integer'},
                                'created_at': {'type': 'string', 'format': 'date-time'}
                            }
                        }
                    },
                    'pagination': {
                        'type': 'object',
                        'properties': {
                            'total': {'type': 'integer'},
                            'pages': {'type': 'integer'},
                            'page': {'type': 'integer'},
                            'per_page': {'type': 'integer'},
                            'next': {'type': 'string', 'nullable': True},
                            'prev': {'type': 'string', 'nullable': True}
                        }
                    }
                }
            }
        },
        401: {'description': 'Non autorisé'},
        403: {'description': 'Permission refusée'},
        500: {'description': 'Erreur serveur'}
    }
})
def get_all_orders_status():
    if request.method == "OPTIONS":
        return build_cors_preflight_response()
        
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)

        # Générer la clé de cache
        cache_key = generate_cache_key("all_orders", page=page, per_page=per_page)
        
        # Vérifier le cache
        cached_result = cache.get(cache_key)
        if cached_result:
            return cors_response(jsonify(cached_result), 200)

        orders_data, pagination = orders_status(page=page, per_page=per_page)

        response_data = {
            "status": "success",
            "data": orders_data,
            "pagination": pagination
        }
        
        # Mettre en cache (2 minutes pour les commandes)
        cache.set(cache_key, response_data, timeout=120)

        return cors_response(response_data, 200)

    except Exception as e:
        error = build_error_response(
            500,
            "Internal Server Error",
            f"Erreur lors de la récupération: {str(e)}",
            request.path
        )
        return cors_response(error, 500)

@app.route("/api/v2/orders/<int:store_id>", methods=["GET"])
@role_required('get_all_orders_of_store')
@swag_from({
    'tags': ['Commandes'],
    'description': 'Récupère les commandes d\'un magasin',
    'parameters': [
        {
            'name': 'store_id',
            'in': 'path',
            'type': 'integer',
            'required': True
        }
    ],
    'responses': {
        200: {'description': 'Liste des commandes du magasin'},
        401: {'description': 'Non autorisé'},
        403: {'description': 'Permission refusée'},
        404: {'description': 'Magasin non trouvé'},
        500: {'description': 'Erreur serveur'}
    }
})
def get_store_orders(store_id):
    if request.method == "OPTIONS":
        return build_cors_preflight_response()

    try:
        # Générer la clé de cache
        cache_key = generate_cache_key(f"store_orders_{store_id}")
        
        # Vérifier le cache
        cached_result = cache.get(cache_key)
        if cached_result:
            return cors_response(jsonify(cached_result), 200)

        orders_data = orders_status(store_id=store_id)

        if not orders_data:
            error = build_error_response(
                404,
                "Not Found",
                f"Aucune commande trouvée pour le magasin {store_id}",
                request.path
            )
            return cors_response(error, 404)

        response_data = {
            "status": "success",
            "data": orders_data,
            "count": len(orders_data)
        }
        
        # Mettre en cache (2 minutes)
        cache.set(cache_key, response_data, timeout=120)

        return cors_response(response_data, 200)

    except Exception as e:
        error = build_error_response(
            500,
            "Internal Server Error",
            f"Erreur lors de la récupération des commandes du magasin {store_id}: {str(e)}",
            request.path
        )
        return cors_response(error, 500)

@app.route("/api/v2/reset", methods=["POST", "OPTIONS"])
# @role_required('reset_database')
@swag_from({
    'tags': ['Administration'],
    'description': 'Réinitialise la base de données',
    'responses': {
        200: {'description': 'Base réinitialisée'},
        401: {'description': 'Non autorisé'},
        403: {'description': 'Permission refusée'},
        500: {'description': 'Erreur de réinitialisation'}
    }
})
def reset_database_route():
    try:
        if request.method == "OPTIONS":
            return jsonify({"status": "success"}), 200
            
        success = reset_database()
        
        if success:
            # Invalider tout le cache après réinitialisation
            invalidate_cache_pattern("*")
            
            return cors_response({
                "status": "success",
                "message": "La base de données a été réinitialisée avec succès"
            }, 200)
        else:
            error = build_error_response(
                500,
                "Internal Server Error",
                "La réinitialisation de la base de données a échoué",
                request.path
            )
            return cors_response(error, 500)
            
    except SQLAlchemyError as e:
        error = build_error_response(
            500,
            "Database Error",
            f"Erreur de base de données: {str(e)}",
            request.path
        )
        return cors_response(error, 500)
        
    except Exception as e:
        error = build_error_response(
            500,
            "Internal Server Error",
            f"Erreur inattendue: {str(e)}",
            request.path
        )
        return cors_response(error, 500)

@app.route("/api/v2/orders/report", methods=["GET"])
@role_required('get_orders_report')
@swag_from({
    'tags': ['Rapports'],
    'description': 'Génère un rapport des commandes',
    'responses': {
        200: {'description': 'Rapport généré'},
        401: {'description': 'Non autorisé'},
        403: {'description': 'Permission refusée'},
        500: {'description': 'Erreur de génération'}
    }
})
def get_orders_report():
    try:
        # Générer la clé de cache
        cache_key = "orders_report"
        
        # Vérifier le cache
        cached_result = cache.get(cache_key)
        if cached_result:
            return cors_response(jsonify(cached_result), 200)

        report_data = generate_orders_report()
        
        if not report_data:
            error = build_error_response(
                500,
                "Internal Server Error",
                "Impossible de générer le rapport",
                request.path
            )
            return cors_response(error, 500)
            
        report = report_data[0]
        
        total_revenue = sum(store['total_revenue'] for store in report['sales_by_store'])
        total_stock = sum(store['total_stock'] for store in report['remaining_stock'])
        
        response = {
            "status": "success",
            "data": {
                "stores_summary": {
                    "count": len(report.get('all_store_ids', [])),
                    "stores_with_orders": len([s for s in report['sales_by_store'] if s['total_orders'] > 0]),
                    "total_revenue": total_revenue,
                    "all_store_ids": report.get('all_store_ids', [])
                },
                "orders_summary": {
                    "total_orders": sum(store['total_orders'] for store in report['sales_by_store']),
                    "completed_orders": sum(store['completed_orders'] for store in report['sales_by_store']),
                    "cancelled_orders": sum(store['cancelled_orders'] for store in report['sales_by_store'])
                },
                "stock_summary": {
                    "total_remaining": total_stock,
                    "low_stock_stores": [store for store in report['remaining_stock'] if store['stock_status'] == 'LOW']
                },
                "detailed_report": report
            }
        }
        
        # Mettre en cache (5 minutes)
        cache.set(cache_key, response, timeout=300)
        
        return cors_response(response, 200)
        
    except SQLAlchemyError as e:
        error = build_error_response(
            500,
            "Database Error",
            f"Erreur de base de données: {str(e)}",
            request.path
        )
        return cors_response(error, 500)
    except Exception as e:
        error = build_error_response(
            500,
            "Internal Server Error",
            f"Erreur inattendue: {str(e)}",
            request.path
        )
        return cors_response(error, 500)

@app.route("/api/v2/products/store/<int:store_id>/restock", methods=["PUT", "OPTIONS"])
@role_required('restock_store')
@swag_from({
    'tags': ['Produits'],
    'description': 'Restocker un magasin',
    'parameters': [
        {
            'name': 'store_id',
            'in': 'path',
            'type': 'integer',
            'required': True
        }
    ],
    'responses': {
        200: {'description': 'Magasin restocké'},
        400: {'description': 'Échec du restock'},
        401: {'description': 'Non autorisé'},
        403: {'description': 'Permission refusée'},
        404: {'description': 'Magasin non trouvé'},
        500: {'description': 'Erreur serveur'}
    }
})
def restock_store_route(store_id):
    if request.method == "OPTIONS":
        return build_cors_preflight_response()

    try:
        success = restock_store_products(store_id)

        # Invalider le cache des produits après restock
        if success:
            invalidate_cache_pattern("all_products:*")
            invalidate_cache_pattern(f"store_products_{store_id}:*")

        if not success: 
            error = build_error_response(
                400,
                "Bad Request",
                f"Le restock du magasin {store_id} a échoué",
                request.path
            )
            return cors_response(error, 400)

        return cors_response({
            "status": "success",
            "message": f"Le magasin {store_id} a été restocké avec succès",
            "store_id": store_id
        }, 200)

    except Exception as e:
        error = build_error_response(
            500,
            "Internal Server Error",
            f"Erreur serveur: {str(e)}",
            request.path
        )
        return cors_response(error, 500)

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8080, debug=True)