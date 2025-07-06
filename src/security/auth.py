from datetime import datetime, timedelta
import jwt
from flask import current_app

def generate_jwt(user_id, username, role, store_id=None):
    payload = {
        'user_id': user_id,
        'username': username,
        'role': role,
        'store_id': store_id,
        'exp': datetime.utcnow() + current_app.config['JWT_EXPIRATION_DELTA']
    }
    return jwt.encode(payload, current_app.config['SECRET_KEY'], algorithm='HS256')

def decode_jwt(token):
    """
    Décode un token JWT avec gestion d'erreurs appropriée
    """
    try:
        # Validation préliminaire du token
        if not token or not isinstance(token, str):
            raise ValueError("Token JWT manquant")
        
        # Vérifier que le token a bien 3 parties (header.payload.signature)
        token_parts = token.split('.')
        if len(token_parts) != 3:
            raise ValueError("Token JWT manquant")
        
        # Vérifier que chaque partie n'est pas vide
        if not all(part.strip() for part in token_parts):
            raise ValueError("Token JWT manquant")
        
        # Décoder le token
        return jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=['HS256'])
        
    except jwt.ExpiredSignatureError:
        raise ValueError("Token JWT expiré")
    except jwt.InvalidTokenError:
        raise ValueError("Token JWT invalide")
    except jwt.DecodeError:
        raise ValueError("Token JWT invalide")
    except Exception as e:
        # Intercepter spécifiquement "Not enough segments"
        if "Not enough segments" in str(e):
            raise ValueError("Token JWT manquant")
        else:
            raise ValueError("Token JWT invalide")