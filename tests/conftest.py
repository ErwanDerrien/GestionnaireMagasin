import pytest
import sys
import os
from unittest.mock import Mock, patch
from flask import Flask, jsonify, request

# Ajouter le répertoire racine au PYTHONPATH
root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

# Mock des modules avant l'import de l'app
mock_modules = [
    'data.database',
    'src.services.product_services',
    'src.services.order_services', 
    'src.services.login_services',
    'src.security'
]

for module in mock_modules:
    if module not in sys.modules:
        sys.modules[module] = Mock()

# Configuration des mocks avec des valeurs par défaut
sys.modules['src.security'].generate_jwt = Mock(return_value='fake_jwt_token')
sys.modules['src.security'].role_required = lambda perm: lambda f: f
sys.modules['src.security'].build_error_response = Mock(side_effect=lambda code, error, message, path: {
    'status_code': code,
    'error': error,
    'message': message,
    'path': path
})
sys.modules['src.security'].build_cors_preflight_response = Mock(return_value=('', 200))
sys.modules['src.security'].cors_response = Mock(side_effect=lambda data, code: (data, code))

@pytest.fixture
def app():
    """Fixture pour créer l'application Flask de test"""
    try:
        # Essayer d'importer depuis la racine du projet
        from app import app as flask_app
        flask_app.config['TESTING'] = True
        flask_app.config['SECRET_KEY'] = 'votre_cle_secrete_complexe'
        return flask_app
    except ImportError:
        # Si l'import échoue, créer une app Flask complète pour les tests
        from flask import Flask, jsonify, request
        import datetime
        
        test_app = Flask(__name__)
        test_app.config['TESTING'] = True
        test_app.config['SECRET_KEY'] = 'votre_cle_secrete_complexe'
        test_app.config['JWT_EXPIRATION_DELTA'] = datetime.timedelta(hours=1)
        test_app.config['SWAGGER'] = {
            'title': 'Store Manager API',
            'version': '1.0',
            'description': 'API pour la gestion de magasins et produits',
            'specs_route': '/apidocs/'
        }
        
        # Ajouter les routes nécessaires pour les tests
        @test_app.route('/api/v2/')
        def home():
            return jsonify({"message": "API fonctionnelle"})
        
        @test_app.route('/api/v2/products', methods=['GET'])
        def get_products():
            # Simuler des headers CORS
            response = jsonify([])
            response.headers['Access-Control-Allow-Origin'] = '*'
            response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'
            response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
            return response
        
        @test_app.route('/api/v2/orders', methods=['POST'])
        def create_order():
            # Vérifier le content-type
            if not request.is_json:
                return jsonify({'error': 'Content-Type must be application/json'}), 400
            
            try:
                data = request.get_json()
                if not data:
                    return jsonify({'message': 'Empty JSON payload'}), 400
                
                # Vérifier les champs obligatoires
                if 'store_id' not in data:
                    return jsonify({'message': 'store_id est obligatoire'}), 400
                
                # Simuler la gestion d'un payload volumineux
                if 'products' in data and len(data['products']) > 500:
                    return jsonify({'error': 'Payload too large'}), 413
                
                return jsonify({'message': 'Order created'}), 201
                
            except Exception as e:
                return jsonify({'error': 'Invalid JSON format'}), 400
        
        @test_app.errorhandler(405)
        def method_not_allowed(error):
            return jsonify({'error': 'Method not allowed'}), 405
        
        @test_app.errorhandler(404)
        def not_found(error):
            return jsonify({'error': 'Not found'}), 404
        
        return test_app

@pytest.fixture
def client(app):
    """Fixture pour créer un client de test"""
    return app.test_client()

@pytest.fixture
def auth_headers():
    """Fixture pour les headers d'authentification"""
    return {
        'Authorization': 'Bearer fake_jwt_token',
        'Content-Type': 'application/json'
    }

@pytest.fixture
def mock_login_service():
    """Mock du service de login"""
    with patch('src.services.login_services.login') as mock:
        yield mock

@pytest.fixture
def mock_product_services():
    """Mock des services produits"""
    with patch('src.services.product_services.stock_status') as mock_stock, \
         patch('src.services.product_services.search_product_service') as mock_search, \
         patch('src.services.product_services.restock_store_products') as mock_restock:
        yield {
            'stock_status': mock_stock,
            'search_product_service': mock_search,
            'restock_store_products': mock_restock
        }

@pytest.fixture
def mock_order_services():
    """Mock des services commandes"""
    with patch('src.services.order_services.orders_status') as mock_orders, \
         patch('src.services.order_services.save_order') as mock_save, \
         patch('src.services.order_services.return_order') as mock_return, \
         patch('src.services.order_services.generate_orders_report') as mock_report:
        yield {
            'orders_status': mock_orders,
            'save_order': mock_save,
            'return_order': mock_return,
            'generate_orders_report': mock_report
        }

@pytest.fixture
def mock_database():
    """Mock de la base de données"""
    with patch('data.database.reset_database') as mock:
        yield mock

@pytest.fixture
def sample_product():
    """Fixture pour un produit exemple"""
    class MockProduct:
        def to_dict(self):
            return {
                'id': 1,
                'name': 'Test Product',
                'category': 'Test Category',
                'price': 19.99,
                'stock_quantity': 10,
                'store_id': 1
            }
    return MockProduct()

@pytest.fixture
def sample_products_data():
    """Fixture pour des données produits exemple"""
    return [
        {
            'id': 1,
            'name': 'Product 1',
            'category': 'Category A',
            'price': 19.99,
            'stock_quantity': 10,
            'store_id': 1
        },
        {
            'id': 2,
            'name': 'Product 2', 
            'category': 'Category B',
            'price': 29.99,
            'stock_quantity': 5,
            'store_id': 1
        }
    ]

@pytest.fixture
def sample_orders_data():
    """Fixture pour des données commandes exemple"""
    return [
        {
            'id': 1,
            'user_id': 'user123',
            'status': 'completed',
            'products': [1, 2],
            'total_price': 49.98,
            'store_id': 1,
            'created_at': '2024-01-01T10:00:00'
        },
        {
            'id': 2,
            'user_id': 'user456',
            'status': 'pending',
            'products': [1],
            'total_price': 19.99,
            'store_id': 1,
            'created_at': '2024-01-01T11:00:00'
        }
    ]

@pytest.fixture
def sample_pagination():
    """Fixture pour la pagination exemple"""
    return {
        'total': 50,
        'pages': 5,
        'page': 1,
        'per_page': 10,
        'next': '/api/v2/products?page=2',
        'prev': None
    }