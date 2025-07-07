from flask import Blueprint, request, jsonify
from flasgger import swag_from
from src.services.product_services import restock_store_products, search_product_service, stock_status
from src.utils.cache_utils import generate_cache_key, invalidate_cache_pattern
from src.utils.extensions import cache
from src.security import build_error_response, build_cors_preflight_response, cors_response
from src.security import role_required
from config.variables import REDIS_PORT

product_bp = Blueprint('product', __name__)

@product_bp.route("/", methods=["GET", "OPTIONS"])
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
        
        cache_key = generate_cache_key("all_products", page=page, per_page=per_page)
        
        cached_result = cache.get(cache_key)
        if cached_result:
            return cors_response(jsonify(cached_result), 200)
        
        products_data, pagination = stock_status(page=page, per_page=per_page)
        
        response_data = {
            "status": "success",
            "data": products_data,
            "pagination": pagination
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
        return cors_response(jsonify(error), 500)

@product_bp.route("/<int:store_id>", methods=["GET", "OPTIONS"])
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

@product_bp.route("/<int:store_id>/<search_term>", methods=["GET", "OPTIONS"])
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

@product_bp.route("/store/<int:store_id>/restock", methods=["PUT", "OPTIONS"])
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
            invalidate_cache_pattern("all_products:*", host='redis', port=REDIS_PORT, db=0, password=None)
            invalidate_cache_pattern(f"store_products_{store_id}:*", host='redis', port=REDIS_PORT, db=0, password=None)

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
