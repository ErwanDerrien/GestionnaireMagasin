from flask import Blueprint, request, jsonify
from data.database import reset_database
from flasgger import swag_from
from sqlalchemy.exc import SQLAlchemyError
from src.utils.cache_utils import invalidate_cache_pattern
from src.security import build_error_response, cors_response
from config.variables import API_MASK, REDIS_PORT, VERSION

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/')
def home():
    return {"message": "API fonctionnelle"}

@admin_bp.route(f'/reset', methods=["POST", "OPTIONS"])
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
            invalidate_cache_pattern("*", host='redis', port=REDIS_PORT, db=0, password=None)
            
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
