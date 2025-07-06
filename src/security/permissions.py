from flask import request, g
from src.security.decorators import jwt_required
from functools import wraps

PERMISSIONS = {
    'employee': [
        'search_product',
        'get_all_products',
        'get_all_products_of_store',
        'save_order',
        'get_all_orders',
        'get_all_orders_of_store',
        'return_order',
        'restock_store'
    ],
    'manager': [
        # Permissions spécifiques aux managers
        'get_orders_report',
        # Toutes les permissions des employés
        'search_product',
        'get_all_products',
        'get_all_products_of_store',
        'save_order',
        'get_all_orders',
        'get_all_orders_of_store',
        'return_order',
        'restock_store'
    ],
    'dev': [
        'test',
        'reset_database'
    ]
}

def role_required(permission):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Vérifier d'abord la présence du token JWT
            token = None
            if 'Authorization' in request.headers:
                token = request.headers['Authorization'].split(" ")[1] if len(request.headers['Authorization'].split(" ")) > 1 else None
            
            if not token:
                from src.security.decorators import build_error_response
                return build_error_response(
                    401,
                    "Unauthorized",
                    "Token JWT manquant",
                    request.path
                )
            
            # Ensuite décoder le token
            try:
                from src.security.auth import decode_jwt
                data = decode_jwt(token)
                g.current_user = data
            except Exception as e:
                from src.security.decorators import build_error_response
                return build_error_response(
                    401,
                    "Unauthorized",
                    str(e),
                    request.path
                )
            
            current_user = getattr(g, 'current_user', None)
            
            if not current_user:
                from src.security.decorators import build_error_response
                return build_error_response(
                    401,
                    "Unauthorized",
                    "Utilisateur non authentifié",
                    request.path
                )
            
            user_role = current_user.get('role')
            
            if user_role == 'dev':
                return f(*args, **kwargs)
            
            if permission not in PERMISSIONS.get(user_role, []):
                from src.security.decorators import build_error_response
                return build_error_response(
                    403,
                    "Forbidden",
                    "Permission refusée, vos permissions sont : " + str(user_role),
                    request.path
                )
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator