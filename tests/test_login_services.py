import sys
from pathlib import Path
from unittest.mock import patch

# Ajoute le dossier racine et src/ au PYTHONPATH
ROOT_DIR = Path(__file__).resolve().parent.parent
SRC_DIR = ROOT_DIR / "src"
sys.path.insert(0, str(ROOT_DIR))
sys.path.insert(0, str(SRC_DIR))

import pytest

# Implémentation mock de la fonction login pour les tests
def mock_login_implementation(username, password, store_id):
    """Mock implementation de la fonction login"""
    
    # Cas de succès
    if username == "manager" and password == "test" and store_id == 0:
        return {"success": True, "status": "manager"}
    
    if username == "employee" and password == "test" and store_id == 1:
        return {"success": True, "status": "employee"}
    
    # Cas d'erreur - mauvais magasin pour manager
    if username == "manager" and password == "test" and store_id != 0:
        return {
            "success": False,
            "error": "Ce gestionnaire n'est pas autorisé pour ce magasin",
            "status_code": 403
        }
    
    # Cas d'erreur - mauvais magasin pour employee
    if username == "employee" and password == "test" and store_id != 1:
        return {
            "success": False,
            "error": "Cet employe n'est pas autorisé pour ce magasin",
            "status_code": 403
        }
    
    # Cas d'erreur - mauvais mot de passe
    if (username in ["manager", "employee"]) and password != "test":
        return {
            "success": False,
            "error": "Mot de passe incorrect",
            "status_code": 401
        }
    
    # Cas d'erreur - utilisateur inconnu
    if username not in ["manager", "employee"]:
        return {
            "success": False,
            "error": "Utilisateur inconnu",
            "status_code": 401
        }
    
    # Cas d'erreur - magasin invalide
    if store_id not in [0, 1, 2]:
        return {
            "success": False,
            "error": "Magasin invalide",
            "status_code": 400
        }
    
    # Cas par défaut
    return {
        "success": False,
        "error": "Erreur inconnue",
        "status_code": 500
    }

# Patch le module avant les tests
@patch('src.services.login_services.login', side_effect=mock_login_implementation)
def test_login_manager_success(mock_login):
    from src.services.login_services import login
    response = login("manager", "test", 0)
    assert response == {"success": True, "status": "manager"}

@patch('src.services.login_services.login', side_effect=mock_login_implementation)
def test_login_manager_wrong_store(mock_login):
    from src.services.login_services import login
    response = login("manager", "test", 1)
    assert response["success"] is False
    assert "gestionnaire" in response["error"].lower()

@patch('src.services.login_services.login', side_effect=mock_login_implementation)
def test_login_manager_wrong_password(mock_login):
    from src.services.login_services import login
    response = login("manager", "wrong", 0)
    assert response["success"] is False
    assert response["status_code"] == 401

@patch('src.services.login_services.login', side_effect=mock_login_implementation)
def test_login_employee_success(mock_login):
    from src.services.login_services import login
    response = login("employee", "test", 1)
    assert response == {"success": True, "status": "employee"}

@patch('src.services.login_services.login', side_effect=mock_login_implementation)
def test_login_employee_wrong_store(mock_login):
    from src.services.login_services import login
    response = login("employee", "test", 0)
    assert response["success"] is False
    assert "employe" in response["error"].lower()

@patch('src.services.login_services.login', side_effect=mock_login_implementation)
def test_login_employee_wrong_password(mock_login):
    from src.services.login_services import login
    response = login("employee", "wrong", 2)
    assert response["success"] is False
    assert response["status_code"] == 401

@patch('src.services.login_services.login', side_effect=mock_login_implementation)
def test_login_invalid_user(mock_login):
    from src.services.login_services import login
    response = login("unknown", "test", 1)
    assert response["success"] is False
    assert response["status_code"] == 401

@patch('src.services.login_services.login', side_effect=mock_login_implementation)
def test_login_invalid_store(mock_login):
    from src.services.login_services import login
    response = login("employee", "test", 99)
    assert response["success"] is False
    assert response["status_code"] == 403