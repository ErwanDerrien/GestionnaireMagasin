from flask import Blueprint, request, jsonify
from flasgger import swag_from
from datetime import timedelta
from src.services.login_services import login
from src.security import generate_jwt, role_required, build_error_response, build_cors_preflight_response, cors_response

auth_bp = Blueprint('auth', __name__)

@auth_bp.route("/login", methods=["POST", "OPTIONS"])
@swag_from({
    'tags': ['Authentification'],
    'description': 'Connexion utilisateur',
    'parameters': [{
        'name': 'body',
        'in': 'body',
        'required': True,
        'schema': {
            'type': 'object',
            'properties': {
                'username': {'type': 'string'},
                'password': {'type': 'string'},
                'store_id': {'type': 'integer'}
            }
        }
    }],
    'responses': {
        200: {'description': 'Connexion réussie'},
        400: {'description': 'Données manquantes'},
        401: {'description': 'Identifiants incorrects'},
        500: {'description': 'Erreur serveur'}
    }
})
def login_route():
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