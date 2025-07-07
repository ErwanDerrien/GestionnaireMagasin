from datetime import datetime
from flask import Blueprint, request, jsonify
from flasgger import swag_from
from sqlalchemy.exc import SQLAlchemyError
from src.services.order_services import generate_orders_report, orders_status, return_order, save_order
from src.utils.cache_utils import generate_cache_key, invalidate_cache_pattern
from src.utils.extensions import cache
from src.security import build_error_response, build_cors_preflight_response, cors_response
from src.security import role_required
from config.variables import REDIS_PORT

order_bp = Blueprint('order', __name__)

@order_bp.route("/", methods=["GET", "OPTIONS"])
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

@order_bp.route("/", methods=["POST", "OPTIONS"])
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
                    'ids': {
                        'type': 'array',
                        'items': {'type': 'integer'},
                        'description': 'Liste des ID de produits avec répétition pour la quantité'
                    }
                },
                'required': ['store_id', 'ids']
            }
        }
    ],
    'responses': {
        201: {
            'description': 'Commande créée',
            'schema': {
                'type': 'object',
                'properties': {
                    'status': {'type': 'string'},
                    'message': {'type': 'string'},
                    'order': {
                        'type': 'object',
                        'properties': {
                            'id': {'type': 'integer'},
                            'total': {'type': 'number'},
                            'products': {
                                'type': 'array',
                                'items': {
                                    'product_id': {'type': 'integer'},
                                    'quantity': {'type': 'integer'}
                                }
                            },
                            'store_id': {'type': 'integer'}
                        }
                    }
                }
            }
        },
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

        # Validation basique
        if not data:
            return build_error_response(
                400,
                "Bad Request",
                "Aucune donnée reçue",
                request.path
            )

        # Validation des champs obligatoires
        required_fields = ['store_id', 'ids']
        if not all(field in data for field in required_fields):
            missing_fields = [field for field in required_fields if field not in data]
            return build_error_response(
                400,
                "Bad Request",
                f"Champs obligatoires manquants: {', '.join(missing_fields)}",
                request.path
            )

        # Validation du type des données
        if not isinstance(data['ids'], list) or not all(isinstance(i, int) for i in data['ids']):
            return build_error_response(
                400,
                "Bad Request",
                "Le champ 'ids' doit être une liste d'entiers",
                request.path
            )

        # Transformation des IDs en produits avec quantité (version corrigée)
        from collections import Counter
        product_quantities = Counter(data['ids'])
        products = [{"product_id": pid, "quantity": qty} for pid, qty in product_quantities.items()]

        # Appel du service
        result = save_order({
            'store_id': data['store_id'],
            'products': products
        })

        # Gestion de la réponse
        if result.get("status") == "success":
            # Invalidation du cache
            invalidate_cache_pattern("all_orders:*", host='redis', port=REDIS_PORT, db=0, password=None)
            invalidate_cache_pattern("all_products:*", host='redis', port=REDIS_PORT, db=0, password=None)
            invalidate_cache_pattern(f"store_products_{data['store_id']}:*", host='redis', port=REDIS_PORT, db=0, password=None)
            
            response_data = {
                "status": "success",
                "message": result.get("message", "Commande enregistrée"),
                "order": {
                    "id": result.get("order_id"),
                    "total": result.get("total"),
                    "products": result.get("products"),
                    "store_id": result.get("store_id")
                }
            }
            return cors_response(jsonify(response_data), 201)

        # Gestion des erreurs métier
        error_type = "Bad Request"
        status_code = 400
        message = result.get("message", "Erreur lors de la commande")
        errors = result.get("errors", [])

        if any("stock insuffisant" in err.lower() for err in errors):
            error_type = "Conflict"
            status_code = 409
        elif any("non trouvé" in err.lower() for err in errors):
            error_type = "Not Found"
            status_code = 404

        error_data = {
            "error": error_type,
            "message": message,
            "path": request.path,
            "status": status_code,
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }
        
        if errors:
            error_data["errors"] = errors
        
        if "store_id" in result:
            error_data["store_id"] = result["store_id"]

        return jsonify(error_data), status_code

    except Exception as e:
        return build_error_response(
            500,
            "Internal Server Error",
            f"Erreur serveur: {str(e)}",
            request.path
        )

@order_bp.route("/<int:store_id>", methods=["GET"])
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

@order_bp.route("/<int:order_id>", methods=["PUT", "OPTIONS"])
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
        invalidate_cache_pattern("all_orders:*", host='redis', port=REDIS_PORT, db=0, password=None)
        invalidate_cache_pattern("all_products:*", host='redis', port=REDIS_PORT, db=0, password=None)

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

@order_bp.route("/report", methods=["GET"])
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
