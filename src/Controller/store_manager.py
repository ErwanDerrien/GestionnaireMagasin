# src/Controller/store_manager.py
from flask import Flask, jsonify, request
from sqlalchemy.exc import SQLAlchemyError
from data.database import reset_database
from src.Services.product_services import search_product_service, stock_status
from src.Services.order_services import orders_status, save_order, return_order

app = Flask(__name__)

@app.route("/login", methods=["POST", "OPTIONS"])
def login_route():
    if request.method == "OPTIONS":
        return _build_cors_preflight_response()
        
    try:
        data = request.get_json()
        if not data:
            return _cors_response({"status": "error", "message": "No data provided"}, 400)
        
        # Logique d'authentification
        if data.get("username") == "manager" and data.get("password") == "test":
            return _cors_response({"status": "success"}, 200)
        else:
            return _cors_response({"status": "fail"}, 401)
            
    except Exception as e:
        return _cors_response({"status": "error", "message": str(e)}, 500)

def _build_cors_preflight_response():
    response = jsonify({"status": "success"})
    response.headers.add("Access-Control-Allow-Credentials", "true")
    response.headers.add("Access-Control-Allow-Origin", "http://localhost:8000")
    response.headers.add("Access-Control-Allow-Headers", 'Access-Control-Allow-Origin, '+ 'Access-Control-Allow-Methods, '+ 'Access-Control-Allow-Headers, '+'Cache-Control, '+'Content-Encoding, '+'Content-Range, '+'Content-Type, '+'Keep-Alive, '+'Location, '+'Vary, '+'X-Amz-Meta-Is-Final')
    response.headers.add("Access-Control-Expose-Headers", 'Access-Control-Allow-Origin, '+ 'Access-Control-Allow-Methods, '+ 'Access-Control-Allow-Headers, '+'Cache-Control, '+'Content-Encoding, '+'Content-Range, '+'Content-Type, '+'Keep-Alive, '+'Location, '+'Vary, '+'X-Amz-Meta-Is-Final')
    response.headers.add("Access-Control-Allow-Methods", "GET, HEAD, POST, PUT, DELETE, CONNECT, OPTIONS, TRACE, PATCH")
    response.headers.add("Access-Control-Max-Age", "86400")
    return response

def _cors_response(data, status_code):
    response = jsonify(data)
    response.headers.add("Access-Control-Allow-Origin", "http://localhost:8000")
    response.headers.add("Access-Control-Allow-Credentials", "true")
    response.headers.add("Content-Type", "application/json")
    return response, status_code

@app.route("/")
def home():
    return {"message": "API fonctionnelle"}

@app.route("/products", methods=["GET"])
def get_all_products_route():
    try:
        products_data = stock_status()
        
        if not products_data:
            return jsonify({
                "status": "success",
                "message": "Aucun produit enregistré",
                "data": {}
            }), 200
            
        return jsonify({
            "status": "success",
            "data": products_data,
            "count": len(products_data)
        }), 200
        
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": f"Erreur lors de la récupération du stock: {str(e)}"
        }), 500

@app.route("/products/<search_term>")
def search_product_route(search_term):
    try:
        products = search_product_service(search_term)
        
        serialized_products = [p.to_dict() for p in products]
        
        return jsonify({
            "status": "success",
            "data": serialized_products,
            "count": len(serialized_products)
        })
    
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

@app.route("/orders", methods=["POST"])
def create_order_route():
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({"status": "error", "message": "No data provided"}), 400
        
        order = save_order(data)
        
        return jsonify({
            "status": "success",
            "message": "Order created successfully",
            "order": order
        }), 201
    
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500
    
@app.route("/orders/<int:order_id>", methods=["PUT"])
def return_order_route(order_id):
    try:
        # Appel à votre service existant
        result = return_order(order_id)
        
        if "erreur" in result.lower() or "non trouvée" in result.lower():
            status_code = 404 if "non trouvée" in result.lower() else 400
            return jsonify({
                "status": "error",
                "message": result
            }), status_code
            
        return jsonify({
            "status": "success",
            "message": result,
            "order_id": order_id
        }), 200
    
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": f"Erreur serveur: {str(e)}"
        }), 500
    
@app.route("/orders", methods=["GET"])
def get_all_orders_status():
    try:
        orders_data = orders_status()
        
        if not orders_data:
            return jsonify({
                "status": "success",
                "message": "Aucune commande trouvée",
                "data": []
            }), 200
            
        return jsonify({
            "status": "success",
            "data": orders_data,
            "count": len(orders_data)
        }), 200
        
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": f"Erreur lors de la récupération: {str(e)}"
        }), 500
    
@app.route("/reset", methods=["POST"])
def reset_database_route():
    try:
        if reset_database():
            return jsonify({
                "status": "success",
                "message": "Base de données réinitialisée",
                "data": {
                    "tables_recréées": True,
                    "données_initiales_insérées": True
                }
            }), 200
        else:
            return jsonify({
                "status": "error",
                "message": "Échec de la réinitialisation"
            }), 500
            
    except SQLAlchemyError as e:
        return jsonify({
            "status": "error",
            "message": f"Erreur SQLAlchemy: {str(e)}"
        }), 500
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": f"Erreur inattendue: {str(e)}"
        }), 500
        
if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8080, debug=True)