from flask import Blueprint, request, jsonify
from flasgger import swag_from
from src.services.product_services import stock_status
from src.utils.cache_utils import generate_cache_key
from src.utils.extensions import cache
from src.security import build_error_response, build_cors_preflight_response, cors_response
from src.security import role_required

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