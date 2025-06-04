"""Module de tests pour order_services.py."""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from data.database import Base, Product, Order
from src.Services import order_services

# Configuration d'une session de test isolée
engine = create_engine("sqlite:///:memory:")
TestingSession = sessionmaker(bind=engine)

@pytest.fixture(scope="function", autouse=True)
def setup_database(monkeypatch):
    """Prépare une base de données temporaire pour chaque test."""
    Base.metadata.create_all(engine)
    test_session = TestingSession()

    # Insère des produits de test
    products = [
        Product(id=1, name="Pain", category="Boulangerie", price=3.00, stock_quantity=10),
        Product(id=2, name="Lait", category="Laitiers", price=2.50, stock_quantity=5),
        Product(id=3, name="Oeufs", category="Frais", price=4.00, stock_quantity=0),
    ]
    test_session.add_all(products)
    test_session.commit()

    # Remplace la session globale par la session de test
    monkeypatch.setattr(order_services, "session", test_session)

    yield

    test_session.close()
    Base.metadata.drop_all(engine)

def test_save_order_success(monkeypatch):
    """Commande réussie."""
    monkeypatch.setattr("builtins.input", lambda _: "o")
    result = order_services.save_order("ev 1,2")
    assert "Commande" in result
    assert "Pain" in result
    assert "Lait" in result

def test_save_order_invalid_format():
    """Commande au format invalide."""
    result = order_services.save_order("ev abc")
    assert "Format invalide" in result

def test_save_order_product_not_found():
    """Commande avec ID inexistant."""
    result = order_services.save_order("ev 99")
    assert "non trouvé" in result

def test_save_order_insufficient_stock():
    """Commande avec un produit en rupture de stock."""
    result = order_services.save_order("ev 3")
    assert "Stock insuffisant" in result

def test_return_order_success(monkeypatch):
    """Annulation d'une commande existante."""
    monkeypatch.setattr("builtins.input", lambda _: "o")
    order_services.save_order("ev 1")
    result = order_services.return_order("gr 1")
    assert "annulée avec succès" in result

def test_return_order_not_found():
    """Commande inexistante."""
    result = order_services.return_order("gr 999")
    assert "non trouvée" in result

def test_return_order_already_cancelled(monkeypatch):
    """Commande déjà annulée."""
    monkeypatch.setattr("builtins.input", lambda _: "o")
    order_services.save_order("ev 2")
    order_services.return_order("gr 1")
    result = order_services.return_order("gr 1")
    assert "déjà annulée" in result

def test_orders_status(monkeypatch):
    """Affichage des commandes."""
    # Simule la confirmation de l'utilisateur
    monkeypatch.setattr("builtins.input", lambda _: "o")

    result = order_services.save_order("ev 1")
    assert "Commande" in result

    result = order_services.orders_status("os")
    assert result is not None
    assert "Pain" in result

def test_orders_status_empty():
    """Aucune commande."""
    result = order_services.orders_status("os")
    assert result is None
