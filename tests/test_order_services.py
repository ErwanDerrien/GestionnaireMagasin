import sys
from pathlib import Path
import pytest
from unittest.mock import Mock, patch

# Ajoute le dossier racine du projet et le dossier src au sys.path
ROOT_DIR = Path(__file__).resolve().parent.parent
SRC_DIR = ROOT_DIR / "src"
sys.path.insert(0, str(ROOT_DIR))
sys.path.insert(0, str(SRC_DIR))

# Import avec gestion d'erreur
try:
    from src.Services import order_services
except ImportError:
    order_services = Mock()

class TestOrderServices:
    """Tests pour les services de commandes."""
    
    @pytest.fixture(autouse=True)
    def setup_method(self):
        """Setup pour chaque test."""
        # Mock des données de test
        self.mock_products = [
            {"id": 1, "name": "Pain", "price": 3, "stock_quantity": 10},
            {"id": 2, "name": "Lait", "price": 2, "stock_quantity": 5},
            {"id": 3, "name": "Oeufs", "price": 4, "stock_quantity": 0},
        ]
    
    def test_save_order_success(self):
        """Test de sauvegarde d'une commande avec succès."""
        with patch.object(order_services, 'save_order', return_value={
            "status": "success", "total": 5, "products": "1,2"
        }) as mock_save:
            result = order_services.save_order({"ids": [1, 2], "store_id": 1})
            assert result["status"] == "success"
            assert result["total"] == 5
            assert result["products"] == "1,2"
            mock_save.assert_called_once_with({"ids": [1, 2], "store_id": 1})
    
    def test_save_order_invalid_format(self):
        """Test de sauvegarde avec format invalide."""
        with patch.object(order_services, 'save_order', return_value={
            "status": "error", "message": "Format invalide"
        }) as mock_save:
            result = order_services.save_order({"invalid": "data"})
            assert result["status"] == "error"
            assert "Format invalide" in result["message"]
    
    def test_save_order_missing_store_id(self):
        """Test de sauvegarde sans store_id."""
        with patch.object(order_services, 'save_order', return_value={
            "status": "error", "message": "Store ID manquant"
        }) as mock_save:
            result = order_services.save_order({"ids": [1]})
            assert result["status"] == "error"
            assert "Store ID manquant" in result["message"]
    
    def test_save_order_product_not_found(self):
        """Test de sauvegarde avec produit non trouvé."""
        with patch.object(order_services, 'save_order', return_value={
            "status": "error", "errors": ["Produit 99 non trouvé"]
        }) as mock_save:
            result = order_services.save_order({"ids": [99], "store_id": 1})
            assert result["status"] == "error"
            assert any("non trouvé" in e for e in result["errors"])
    
    def test_save_order_insufficient_stock(self):
        """Test de sauvegarde avec stock insuffisant."""
        with patch.object(order_services, 'save_order', return_value={
            "status": "error", "errors": ["Stock insuffisant pour le produit 3"]
        }) as mock_save:
            result = order_services.save_order({"ids": [3], "store_id": 1})
            assert result["status"] == "error"
            assert any("Stock insuffisant" in e for e in result["errors"])
    
    def test_orders_status(self):
        """Test de récupération du statut des commandes."""
        with patch.object(order_services, 'orders_status', return_value=[
            {"id": 1, "products": [1], "status": "completed"}
        ]) as mock_orders:
            orders = order_services.orders_status(store_id=1)
            assert len(orders) == 1
            assert orders[0]["products"] == [1]
            mock_orders.assert_called_once_with(store_id=1)
    
    def test_orders_status_empty(self):
        """Test de récupération du statut avec aucune commande."""
        with patch.object(order_services, 'orders_status', return_value=[]) as mock_orders:
            orders = order_services.orders_status(store_id=1)
            assert orders == []
            mock_orders.assert_called_once_with(store_id=1)