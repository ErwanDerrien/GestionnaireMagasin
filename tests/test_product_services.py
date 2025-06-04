"""Module de tests pour product_services.py."""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from data.database import Base, Product
from src.Services.product_services import search_product, stock_status
from src.Views.console_view import format_products

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
        Product(id=1, name="Bananes", category="Fruits", price=1.99, stock_quantity=50),
        Product(id=2, name="Pommes", category="Fruits", price=2.49, stock_quantity=100),
        Product(id=3, name="Carottes", category="Légumes", price=1.49, stock_quantity=80),
    ]
    test_session.add_all(products)
    test_session.commit()

    # Remplace la session globale par la session de test
    import src.Services.product_services as product_services
    monkeypatch.setattr(product_services, "session", test_session)

    yield

    test_session.close()
    Base.metadata.drop_all(engine)

def test_search_product_by_id():
    """Recherche un produit par ID."""
    result = search_product("sr 1")
    assert "Bananes" in result

def test_search_product_by_name():
    """Recherche un produit par nom."""
    result = search_product("sr Pommes")
    assert "Pommes" in result

def test_search_product_by_category():
    """Recherche un produit par catégorie."""
    result = search_product("sr Légumes")
    assert "Carottes" in result

def test_search_product_not_found():
    """Recherche un produit inexistant."""
    result = search_product("sr Chocolat")
    assert result == "Aucun produit trouvé."

def test_stock_status():
    """Teste que le stock retourne bien les produits formatés en dictionnaire."""
    stock = stock_status("st")
    assert isinstance(stock, dict)
    assert stock["Bananes"]["stock"] == 50
    assert stock["Pommes"]["price"] == 2.49

def test_stock_status_empty(monkeypatch):
    """Teste le cas où la base est vide."""
    # Vide la base
    import src.Services.product_services as product_services
    product_services.session.query(Product).delete()
    product_services.session.commit()
    stock = stock_status("st")
    assert stock is None
