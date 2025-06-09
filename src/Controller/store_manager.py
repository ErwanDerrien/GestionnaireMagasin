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
        
        if data.get("username") == "manager" and data.get("password") == "test":
            return _cors_response({"status": "manager"}, 200)
        elif data.get("username") == "employee" and data.get("password") == "test":
            return _cors_response({"status": "employee"}, 200)
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

@app.route("/products", methods=["GET", "OPTIONS"])
def get_all_products_route():
    if request.method == "OPTIONS":
        return _build_cors_preflight_response()
        
    try:
        products_data = stock_status()
        
        return _cors_response({
            "status": "success",
            "data": products_data,
            "count": len(products_data)
        }, 200)
        
    except Exception as e:
        return _cors_response({
            "status": "error",
            "message": f"Erreur lors de la récupération du stock: {str(e)}"
        }, 500)

@app.route("/products/<search_term>", methods=["GET", "OPTIONS"])
def search_product_route(search_term):
    if request.method == "OPTIONS":
        return _build_cors_preflight_response()
        
    try:
        products = search_product_service(search_term)
        serialized_products = [p.to_dict() for p in products]
        
        response_data = {
            "status": "success",
            "data": serialized_products,
            "count": len(serialized_products),
            "message": "Aucun produit trouvé" if not serialized_products else None
        }
        
        return _cors_response(response_data, 200)
    
    except Exception as e:
        return _cors_response({
            "status": "error",
            "message": str(e),
            "data": [],
            "count": 0
        }, 500)

@app.route("/orders", methods=["POST", "OPTIONS"])
def create_order_route():
    if request.method == "OPTIONS":
        return _build_cors_preflight_response()

    try:
        data = request.get_json()

        if not data:
            return _cors_response({
                "status": "error",
                "message": "Aucune donnée reçue"
            }, 400)

        result = save_order(data)

        if result.get("status") == "success":
            return _cors_response({
                "status": "success",
                "message": result.get("message", "Commande enregistrée"),
                "order": {
                    "id": result.get("order_id"),
                    "total": result.get("total"),
                    "products": result.get("products")
                }
            }, 201)

        elif result.get("status") == "error":
            message = result.get("message", "Erreur lors de la commande")
            errors = result.get("errors", [])

            # Si le message indique un problème de stock
            if "stock épuisé" in " ".join(errors).lower() or "stock" in message.lower():
                return _cors_response({
                    "status": "error",
                    "message": message,
                    "errors": errors
                }, 409)  # 409 Conflict pour stock insuffisant

            return _cors_response({
                "status": "error",
                "message": message,
                "errors": errors
            }, 400)

        # Cas inattendu
        return _cors_response({
            "status": "error",
            "message": "Réponse du service inattendue"
        }, 500)

    except Exception as e:
        return _cors_response({
            "status": "error",
            "message": f"Erreur serveur: {str(e)}"
        }, 500)
    
@app.route("/orders/<int:order_id>", methods=["PUT", "OPTIONS"])
def return_order_route(order_id):
    if request.method == "OPTIONS":
        return _build_cors_preflight_response()

    try:
        result = return_order(order_id)

        if "erreur" in result.lower() or "non trouvée" in result.lower():
            status_code = 404 if "non trouvée" in result.lower() else 400
            return _cors_response({
                "status": "error",
                "message": result
            }, status_code)

        return _cors_response({
            "status": "success",
            "message": result,
            "order_id": order_id
        }, 200)

    except Exception as e:
        return _cors_response({
            "status": "error",
            "message": f"Erreur serveur: {str(e)}"
        }, 500)

    
@app.route("/orders", methods=["GET"])
def get_all_orders_status():
    try:
        orders_data = orders_status()

        if not orders_data:
            return _cors_response({
                "status": "success",
                "message": "Aucune commande trouvée",
                "data": []
            }, 200)

        return _cors_response({
            "status": "success",
            "data": orders_data,
            "count": len(orders_data)
        }, 200)

    except Exception as e:
        return _cors_response({
            "status": "error",
            "message": f"Erreur lors de la récupération: {str(e)}"
        }, 500)
    
@app.route("/reset", methods=["POST", "OPTIONS"])
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