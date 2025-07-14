import json
import os
from typing import Dict, Any

class Variables:
    def __init__(self):
        self._vars = self._load_variables()
    
    def _load_variables(self) -> Dict[str, Any]:
        """Charger les variables depuis le fichier JSON"""
        try:
            file_path = os.path.join(os.path.dirname(__file__), 'universal_variables.json')
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"Erreur lors du chargement des variables: {e}")
            return {}
    
    @property
    def HOST(self) -> str:
        return self._vars.get('host', '')
    @property
    def APP_PORT(self) -> str:
        return self._vars.get('app_port', '')
    @property
    def API_MASK(self) -> str:
        return self._vars.get('api_mask', '')
    @property
    def VERSION(self) -> str:
        return self._vars.get('version', '')
    @property
    def PROMETHEUS_PORT(self) -> str:
        return self._vars.get('prometheus_port', '')
    @property
    def REDIS_PORT(self) -> str:
        return self._vars.get('redis_port', '')
    @property
    def REDIS_EXPORTER_PORT(self) -> str:
        return self._vars.get('redis_exporter_port', '')
    @property
    def AUTH_SERVICE(self) -> str:
        return self._vars.get('auth_service', '')
    @property
    def PRODUCTS_SERVICE(self) -> str:
        return self._vars.get('products_service', '')
    @property
    def ORDERS_SERVICE(self) -> str:
        return self._vars.get('orders_service', '')

# Instance globale
vars = Variables()

# Exporter les variables pour un accès direct
HOST = vars.HOST
APP_PORT = vars.APP_PORT
API_MASK = vars.API_MASK
VERSION = vars.VERSION
PROMETHEUS_PORT = vars.PROMETHEUS_PORT
REDIS_PORT = vars.REDIS_PORT
REDIS_EXPORTER_PORT = vars.REDIS_EXPORTER_PORT
AUTH_SERVICE = vars.AUTH_SERVICE
PRODUCTS_SERVICE = vars.PRODUCTS_SERVICE
ORDERS_SERVICE = vars.ORDERS_SERVICE

# Usage:
# from variables import HOST, APP_PORT, API_MASK, VERSION, PROMETHEUS_PORT, REDIS_PORT, REDIS_EXPORTER_PORT, AUTH_SERVICE, PRODUCTS_SERVICE, ORDERS_SERVICE
# print(HOST)  # "localhost"
# print(APP_PORT)  # "8080"
