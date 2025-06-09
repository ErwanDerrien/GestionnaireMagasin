# src/Controller/store_manager.py
from flask import Flask, jsonify, request
from sqlalchemy.exc import SQLAlchemyError
from data.database import reset_database
from src.Services.product_services import restock_store_products, search_product_service, stock_status
from src.Services.order_services import orders_status, save_order, return_order, generate_orders_report
from src.Services.login_services import login

app = Flask(__name__)

@app.route("/login", methods=["POST", "OPTIONS"])
def login_route():
    if request.method == "OPTIONS":
        return _build_cors_preflight_response()
        
    try:
        data = request.get_json()
        if not data:
            return _cors_response({"status": "error", "message": "No data provided"}, 400)

        username = data.get("username")
        password = data.get("password")
        store_id = data.get("store_id")

        result = login(username, password, store_id)

        if result.get("success"):
            return _cors_response({"status": result["status"]}, 200)
        else:
            return _cors_response(
                {"status": "error", "message": result["error"]}, result["status_code"]
            )

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

@app.route("/products/<int:store_id>", methods=["GET", "OPTIONS"])
def get_all_products_of_store_route(store_id):
    if request.method == "OPTIONS":
        return _build_cors_preflight_response()
        
    try:
        products_data = stock_status(store_id)
        
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


@app.route("/products/<store_id>/<search_term>", methods=["GET", "OPTIONS"])
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

        # Validation supplémentaire du store_id
        if 'store_id' not in data:
            return _cors_response({
                "status": "error",
                "message": "Le champ 'store_id' est obligatoire"
            }, 400)

        result = save_order(data)

        if result.get("status") == "success":
            return _cors_response({
                "status": "success",
                "message": result.get("message", "Commande enregistrée"),
                "order": {
                    "id": result.get("order_id"),
                    "total": result.get("total"),
                    "products": result.get("products"),
                    "store_id": result.get("store_id")
                }
            }, 201)

        elif result.get("status") == "error":
            message = result.get("message", "Erreur lors de la commande")
            errors = result.get("errors", [])
            store_id = result.get("store_id")

            response = {
                "status": "error",
                "message": message,
                "errors": errors,
                "store_id": store_id
            }

            # Gestion des codes d'erreur spécifiques
            if any("stock insuffisant" in err.lower() for err in errors):
                return _cors_response(response, 409)
            elif any("non trouvé" in err.lower() for err in errors):
                return _cors_response(response, 404)
            else:
                return _cors_response(response, 400)

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
        if request.method == "OPTIONS":
            return jsonify({"status": "success"}), 200
            
        success = reset_database()
        
        if success:
            response = {
                "status": "success",
                "message": "La base de données a été réinitialisée avec succès",
                "details": {
                    "actions": [
                        "Tables supprimées et recréées",
                        "Données initiales insérées",
                        "Exemple de commande ajoutée"
                    ],
                    "counts": {
                        "produits_ajoutés": 9,
                        "commandes_ajoutées": 1
                    }
                }
            }
            return jsonify(response), 200
        else:
            response = {
                "status": "error",
                "message": "La réinitialisation de la base de données a échoué",
                "suggestion": "Vérifiez les logs du serveur pour plus de détails",
                "possible_causes": [
                    "Problème de connexion à la base de données",
                    "Erreur de validation des données",
                    "Problème de permissions"
                ]
            }
            return jsonify(response), 500
            
    except SQLAlchemyError as e:
        error_response = {
            "status": "error",
            "message": "Erreur de base de données",
            "technical_details": str(e),
            "type": "database_error",
            "action_required": "Contactez l'administrateur système"
        }
        return jsonify(error_response), 500
        
    except Exception as e:
        error_response = {
            "status": "error",
            "message": "Erreur inattendue",
            "technical_details": str(e),
            "type": "unexpected_error",
            "action_required": "Contactez le support technique"
        }
        return jsonify(error_response), 500

@app.route("/orders/report", methods=["GET"])
def get_orders_report():
    try:
        report_data = generate_orders_report()
        
        if not report_data:
            return _cors_response({
                "status": "error",
                "message": "Impossible de générer le rapport",
                "suggestion": "Vérifiez les logs du serveur"
            }, 500)
            
        report = report_data[0]
        
        # Calcul des résumés globaux
        total_revenue = sum(store['total_revenue'] for store in report['sales_by_store'])
        total_stock = sum(store['total_stock'] for store in report['remaining_stock'])
        
        # Formatage de la réponse
        response = {
            "status": "success",
            "data": {
                "stores_summary": {
                    "count": len(report.get('all_store_ids', [])),
                    "stores_with_orders": len([s for s in report['sales_by_store'] if s['total_orders'] > 0]),
                    "total_revenue": total_revenue,
                    "all_store_ids": report.get('all_store_ids', [])
                },
                "orders_summary": {
                    "total_orders": sum(store['total_orders'] for store in report['sales_by_store']),
                    "completed_orders": sum(store['completed_orders'] for store in report['sales_by_store']),
                    "cancelled_orders": sum(store['cancelled_orders'] for store in report['sales_by_store'])
                },
                "stock_summary": {
                    "total_remaining": total_stock,
                    "low_stock_stores": [store for store in report['remaining_stock'] if store['stock_status'] == 'LOW']
                },
                "detailed_report": report
            }
        }
        
        return _cors_response(response, 200)
        
    except SQLAlchemyError as e:
        return _cors_response({
            "status": "error",
            "message": "Database error",
            "details": str(e)
        }, 500)
    except Exception as e:
        return _cors_response({
            "status": "error",
            "message": "Unexpected error",
            "details": str(e)
        }, 500)
     
@app.route("/products/store/<int:store_id>/restock", methods=["PUT", "OPTIONS"])
def restock_store_route(store_id):
    if request.method == "OPTIONS":
        return _build_cors_preflight_response()

    try:
        success = restock_store_products(store_id)

        if not success:
            return _cors_response({
                "status": "error",
                "message": f"Le restock du magasin {store_id} a échoué."
            }, 400)

        return _cors_response({
            "status": "success",
            "message": f"Le magasin {store_id} a été restocké avec succès.",
            "store_id": store_id
        }, 200)

    except Exception as e:
        return _cors_response({
            "status": "error",
            "message": f"Erreur serveur: {str(e)}"
        }, 500)
        
if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8080, debug=True)