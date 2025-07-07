import json
import hashlib
from typing import Dict, Any
from config.variables import REDIS_PORT
        
def generate_cache_key(prefix, **kwargs):
    """Génère une clé de cache unique basée sur les paramètres"""
    key_data = json.dumps(kwargs, sort_keys=True)
    key_hash = hashlib.md5(key_data.encode()).hexdigest()
    return f"{prefix}:{key_hash}"

def invalidate_cache_pattern(pattern, host='localhost', port=REDIS_PORT, db=0, password=None):
    """Invalide les clés de cache correspondant à un pattern"""
    try:
        redis_client = redis.Redis(
            host=host,
            port=port,
            db=db,
            password=password
        )
        keys = list(redis_client.scan_iter(pattern))
        if keys:
            redis_client.delete(*keys)
            print(f"Cache invalidé pour le pattern: {pattern}, {len(keys)} clés supprimées")
    except Exception as e:
        print(f"Erreur lors de l'invalidation du cache: {str(e)}")