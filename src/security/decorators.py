from functools import wraps
from flask import request, g, jsonify, request
from datetime import datetime


def jwt_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if request.method == "OPTIONS":
            return f(*args, **kwargs)
            
        token = None
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            
            # Vérifier le format "Bearer <token>"
            if auth_header.startswith('Bearer '):
                token_part = auth_header[7:].strip()  # Supprimer "Bearer " et espaces
                if token_part:
                    token = token_part
            else:
                return build_error_response(
                    401,
                    "Unauthorized",
                    "Format d'autorisation invalide",
                    request.path
                )
        
        if not token:
            return build_error_response(
                401,
                "Unauthorized",
                "Token JWT manquant",
                request.path
            )
        
        # Validation supplémentaire : vérifier que le token a au moins 3 parties (header.payload.signature)
        if len(token.split('.')) < 3:
            return build_error_response(
                401,
                "Unauthorized",
                "Token JWT manquant",
                request.path
            )
        
        try:
            from src.security.auth import decode_jwt  # Import local pour éviter la circularité
            data = decode_jwt(token)
            g.current_user = data
        except Exception as e:
            # Intercepter spécifiquement l'erreur "Not enough segments"
            error_message = str(e)
            if "Not enough segments" in error_message or "not enough values to unpack" in error_message.lower():
                error_message = "Token JWT invalide ou malformé"
            elif "Signature has expired" in error_message:
                error_message = "Token JWT expiré"
            elif "Invalid token" in error_message or "decode" in error_message.lower():
                error_message = "Token JWT invalide"
            
            return build_error_response(
                401,
                "Unauthorized",
                error_message,
                request.path
            )
        
        return f(*args, **kwargs)
    return decorated_function

def build_error_response(status_code, error_type, message, path):
    """Construit une réponse d'erreur avec CORS - retourne directement une Response Flask"""
    error_data = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "status": status_code,
        "error": error_type,
        "message": message,
        "path": path
    }
    
    response = jsonify(error_data)
    response.status_code = status_code
    
    # Headers CORS
    response.headers.add("Access-Control-Allow-Origin", "http://localhost:8000")
    response.headers.add("Access-Control-Allow-Credentials", "true")
    response.headers.add("Content-Type", "application/json")
    
    return response

def build_cors_preflight_response():
    response = jsonify({"status": "success"})
    response.headers.add("Access-Control-Allow-Credentials", "true")
    response.headers.add("Access-Control-Allow-Origin", "http://localhost:8000")
    response.headers.add("Access-Control-Allow-Headers", 'Access-Control-Allow-Origin, '+ 'Access-Control-Allow-Methods, '+ 'Access-Control-Allow-Headers, '+'Cache-Control, '+'Content-Encoding, '+'Content-Range, '+'Content-Type, '+'Keep-Alive, '+'Location, '+'Vary, '+'X-Amz-Meta-Is-Final')
    response.headers.add("Access-Control-Expose-Headers", 'Access-Control-Allow-Origin, '+ 'Access-Control-Allow-Methods, '+ 'Access-Control-Allow-Headers, '+'Cache-Control, '+'Content-Encoding, '+'Content-Range, '+'Content-Type, '+'Keep-Alive, '+'Location, '+'Vary, '+'X-Amz-Meta-Is-Final')
    response.headers.add("Access-Control-Allow-Methods", "GET, HEAD, POST, PUT, DELETE, CONNECT, OPTIONS, TRACE, PATCH")
    response.headers.add("Access-Control-Max-Age", "86400")
    return response

def cors_response(data, status_code):
    """Construit une réponse avec headers CORS"""
    # Si data est déjà un objet Response, on ajoute juste les headers CORS
    if hasattr(data, 'headers') and hasattr(data, 'status_code'):
        # C'est déjà un objet Response Flask
        data.headers.add("Access-Control-Allow-Origin", "http://localhost:8000")
        data.headers.add("Access-Control-Allow-Credentials", "true")
        data.headers.add("Content-Type", "application/json")
        return data
    
    # Sinon, on crée une nouvelle response
    response = jsonify(data)
    response.status_code = status_code
    response.headers.add("Access-Control-Allow-Origin", "http://localhost:8000")
    response.headers.add("Access-Control-Allow-Credentials", "true")
    response.headers.add("Content-Type", "application/json")
    return response