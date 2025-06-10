import sys
from pathlib import Path

# Ajoute le dossier racine et src/ au PYTHONPATH
ROOT_DIR = Path(__file__).resolve().parent.parent
SRC_DIR = ROOT_DIR / "src"
sys.path.insert(0, str(ROOT_DIR))
sys.path.insert(0, str(SRC_DIR))

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from data.database import Base
from src.Models.product import Product
import src.Services.product_services as product_services
from src.DAO import product_dao

# Configuration de la base de données en mémoire
engine = create_engine("sqlite:///:memory:")
TestingSession = sessionmaker(bind=engine)

@pytest.fixture(scope="function", autouse=True)
def setup_database(monkeypatch):
    """Prépare une base SQLite temporaire pour chaque test."""
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    test_session = TestingSession()

    # Données de test
    products = [
        Product(id=1, name="Bananes", category="Fruits", price=199, stock_quantity=50, store_id=1, max_quantity=100),
        Product(id=2, name="Pommes", category="Fruits", price=249, stock_quantity=100, store_id=1, max_quantity=100),
        Product(id=3, name="Carottes", category="Légumes", price=149, stock_quantity=80, store_id=1, max_quantity=100),
    ]
    test_session.add_all(products)
    test_session.commit()

    # Redirige la fonction query() de product_dao vers la session de test
    monkeypatch.setattr(product_dao, "query", lambda model: test_session.query(model))

    yield

    test_session.close()
    Base.metadata.drop_all(engine)

def test_search_product_not_found():
    """Recherche un produit inexistant."""
    result = product_services.search_product_service("Chocolat")
    assert result == []
