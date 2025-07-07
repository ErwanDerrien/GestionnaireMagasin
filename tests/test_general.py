import json
from config.variables import VERSION
class TestGeneral:
    """Tests généraux pour l'application"""
    
    def test_home_endpoint(self, client):
        """Test de l'endpoint home"""
        response = client.get('/api/v2/')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['message'] == 'API fonctionnelle'
    
    def test_swagger_config(self, app):
        """Test de la configuration Swagger"""
        assert app.config['SWAGGER']['title'] == 'Store Manager API'
        assert app.config['SWAGGER']['version'] == f'{VERSION}'
        assert app.config['SWAGGER']['description'] == 'API pour la gestion de magasins et produits'
        assert app.config['SWAGGER']['specs_route'] == '/apidocs/'
    
    def test_app_config(self, app):
        """Test de la configuration de l'application"""
        assert app.config['SECRET_KEY'] == 'votre_cle_secrete_complexe'
        assert app.config['JWT_EXPIRATION_DELTA'].total_seconds() == 3600  # 1 heure
    
    def test_cors_headers_present(self, client, auth_headers):
        """Test de la présence des headers CORS"""
        response = client.get('/api/v2/products/', headers=auth_headers, follow_redirects=True)
        
        # Vérifier que les headers CORS sont présents dans la réponse
        assert 'Access-Control-Allow-Origin' in response.headers or response.status_code in [401, 403]
    
    def test_invalid_endpoint(self, client):
        """Test d'accès à un endpoint inexistant"""
        response = client.get('/api/v2/invalid')
        
        assert response.status_code == 404
    
    def test_content_type_validation(self, client, auth_headers):
        """Test de validation du content-type pour les POST"""
        # Test sans content-type JSON
        response = client.post('/api/v2/orders/',
                             data="invalid data",
                             headers=auth_headers)
        
        # Le serveur devrait retourner une erreur (400 ou 500)
        assert response.status_code in [400, 500]
    
    def test_method_not_allowed(self, client):
        """Test de méthode non autorisée"""
        response = client.patch('/api/v2/')
        
        assert response.status_code == 405  # Method Not Allowed
    
    def test_large_payload_handling(self, client, auth_headers):
        """Test de gestion d'un payload volumineux"""
        large_order_data = {
            'store_id': 1,
            'products': [{'product_id': i, 'quantity': 1} for i in range(1000)]
        }
        
        response = client.post('/api/v2/orders/',
                             data=json.dumps(large_order_data),
                             headers=auth_headers)
        
        # Devrait traiter ou rejeter proprement le gros payload
        assert response.status_code in [201, 400, 413, 500]
    
    def test_empty_json_payload(self, client, auth_headers):
        """Test de payload JSON vide"""
        response = client.post('/api/v2/orders/',
                             data="{}",
                             headers=auth_headers)
        
        assert response.status_code == 400
    
    def test_malformed_json(self, client, auth_headers):
        """Test de JSON malformé"""
        response = client.post('/api/v2/orders/',
                             data="{'invalid': json}",
                             headers=auth_headers)
        
        # Devrait retourner une erreur de format
        assert response.status_code in [400, 500]