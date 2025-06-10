import sys
from pathlib import Path

# Ajoute le dossier racine du projet et le dossier src au sys.path
ROOT_DIR = Path(__file__).resolve().parent.parent
SRC_DIR = ROOT_DIR / "src"
sys.path.insert(0, str(ROOT_DIR))
sys.path.insert(0, str(SRC_DIR))

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from data.database import Base
from src.Models.product import Product
from src.Models.order import Order
from src.Services import order_services

# Configuration de la base de données en mémoire
engine = create_engine("sqlite:///:memory:")
TestingSession = sessionmaker(bind=engine)

@pytest.fixture(scope="function", autouse=True)
def setup_database(monkeypatch):
    """Prépare une base SQLite temporaire pour chaque test."""
    Base.metadata.create_all(engine)
    test_session = TestingSession()

    # Données de test
    products = [
        Product(id=1, name="Pain", category="Boulangerie", price=3, stock_quantity=10, store_id=1, max_quantity=20),
        Product(id=2, name="Lait", category="Laitiers", price=2, stock_quantity=5, store_id=1, max_quantity=20),
        Product(id=3, name="Oeufs", category="Frais", price=4, stock_quantity=0, store_id=1, max_quantity=20),
    ]
    test_session.add_all(products)
    test_session.commit()

    # Redirige la session globale vers la session de test
    monkeypatch.setattr(order_services, "session", test_session)

    yield

    test_session.close()
    Base.metadata.drop_all(engine)

def test_save_order_success():
    result = order_services.save_order({"ids": [1, 2], "store_id": 1})
    assert result["status"] == "success"
    assert result["total"] == 5
    assert result["products"] == "1,2"

def test_save_order_invalid_format():
    result = order_services.save_order({"invalid": "data"})
    assert result["status"] == "error"
    assert "Format invalide" in result["message"]

def test_save_order_missing_store_id():
    result = order_services.save_order({"ids": [1]})
    assert result["status"] == "error"
    assert "Store ID manquant" in result["message"]

def test_save_order_product_not_found():
    result = order_services.save_order({"ids": [99], "store_id": 1})
    assert result["status"] == "error"
    assert any("non trouvé" in e for e in result["errors"])

def test_save_order_insufficient_stock():
    result = order_services.save_order({"ids": [3], "store_id": 1})
    assert result["status"] == "error"
    assert any("Stock insuffisant" in e for e in result["errors"])

def test_orders_status():
    order_services.save_order({"ids": [1], "store_id": 1})
    orders = order_services.orders_status(store_id=1)
    assert len(orders) == 1
    assert orders[0]["products"] == [1]

def test_orders_status_empty():
    orders = order_services.orders_status(store_id=1)
    assert orders == []
