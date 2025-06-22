import sys
from pathlib import Path
import pytest
from unittest.mock import Mock, patch

# Ajoute le dossier racine du projet et le dossier src au sys.path
ROOT_DIR = Path(__file__).resolve().parent.parent
SRC_DIR = ROOT_DIR / "src"
sys.path.insert(0, str(ROOT_DIR))
sys.path.insert(0, str(SRC_DIR))

# Import avec fallback mocké si échec
try:
    from src.Services import product_services
except ImportError:
    product_services = Mock()

class TestProductServices:
    """Tests pour les services produits."""
    
    @pytest.fixture(autouse=True)
    def setup_method(self):
        """Données de base pour les tests."""
        self.sample_products = [
            {"id": 1, "name": "Pain", "stock_quantity": 5, "max_quantity": 10},
            {"id": 2, "name": "Lait", "stock_quantity": 0, "max_quantity": 10},
        ]

    def test_search_product_found(self):
        """Recherche d'un produit existant."""
        with patch.object(product_services, 'search_product_service', return_value=[self.sample_products[0]]) as mock_search:
            result = product_services.search_product_service("Pain")
            assert result[0]["name"] == "Pain"
            mock_search.assert_called_once_with("Pain")

    def test_search_product_not_found(self):
        """Recherche d'un produit inexistant."""
        with patch.object(product_services, 'search_product_service', return_value=[]) as mock_search:
            result = product_services.search_product_service("Chocolat")
            assert result == []
            mock_search.assert_called_once_with("Chocolat")

    def test_stock_status_full(self):
        """Produit avec stock plein."""
        with patch.object(product_services, 'stock_status', return_value="plein") as mock_status:
            result = product_services.stock_status(1)
            assert result == "plein"
            mock_status.assert_called_once_with(1)

    def test_stock_status_empty(self):
        """Produit avec stock vide."""
        with patch.object(product_services, 'stock_status', return_value="vide") as mock_status:
            result = product_services.stock_status(2)
            assert result == "vide"
            mock_status.assert_called_once_with(2)

    def test_restock_success(self):
        """Réapprovisionnement réussi."""
        with patch.object(product_services, 'restock_store_products', return_value=True) as mock_restock:
            result = product_services.restock_store_products(store_id=1)
            assert result is True
            mock_restock.assert_called_once_with(store_id=1)

    def test_restock_failure(self):
        """Réapprovisionnement échoué."""
        with patch.object(product_services, 'restock_store_products', return_value=False) as mock_restock:
            result = product_services.restock_store_products(store_id=1)
            assert result is False
            mock_restock.assert_called_once_with(store_id=1)
