# tests/test_login_services.py

import sys
from pathlib import Path

# Ajoute le dossier racine et src/ au PYTHONPATH
ROOT_DIR = Path(__file__).resolve().parent.parent
SRC_DIR = ROOT_DIR / "src"
sys.path.insert(0, str(ROOT_DIR))
sys.path.insert(0, str(SRC_DIR))

import pytest
from src.Services.login_services import login

def test_login_manager_success():
    response = login("manager", "test", 0)
    assert response == {"success": True, "status": "manager"}

def test_login_manager_wrong_store():
    response = login("manager", "test", 1)
    assert response["success"] is False
    assert "gestionnaire" in response["error"].lower()

def test_login_manager_wrong_password():
    response = login("manager", "wrong", 0)
    assert response["success"] is False
    assert response["status_code"] == 401

def test_login_employee_success():
    response = login("employee", "test", 1)
    assert response == {"success": True, "status": "employee"}

def test_login_employee_wrong_store():
    response = login("employee", "test", 0)
    assert response["success"] is False
    assert "employe" in response["error"].lower()

def test_login_employee_wrong_password():
    response = login("employee", "wrong", 2)
    assert response["success"] is False
    assert response["status_code"] == 401

def test_login_invalid_user():
    response = login("unknown", "test", 1)
    assert response["success"] is False
    assert response["status_code"] == 401

def test_login_invalid_store():
    response = login("employee", "test", 99)
    assert response["success"] is False
    assert response["status_code"] == 400
