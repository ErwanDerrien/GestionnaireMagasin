# src/Controller/store_manager.py
from flask import Flask, jsonify, request
from data.database import session, Base, engine
from src.Models.product import Product
from src.Services.product_services import search_product_service, stock_status
from src.Services.order_services import orders_status, save_order, return_order
from src.Views.console_view import (
    display_welcome_message,
    display_goodbye_message,
    display_error,
    display_stock,
    display_message,
    prompt_reset_database,
    prompt_command,
    display_products,
    format_products,
    format_orders,
)

app = Flask(__name__)

def run_api():
    app.run(host="0.0.0.0", port=8080, debug=True)

@app.route("/")
def home():
    return {"message": "API fonctionnelle"}

@app.route("/product/<search_term>")
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

@app.route("/order", methods=["POST"])
def create_order_route():
    try:
        data = request.get_json()
        
        # Validation basique des données
        if not data:
            return jsonify({"status": "error", "message": "No data provided"}), 400
        
        # Appel à votre service existant
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
    
@app.route("/order/<int:order_id>", methods=["PUT"])  # PUT est plus standard qu'UPDATE
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
    
@app.route("/order", methods=["GET"])
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
    

def analyse_input(user_input: str) -> str:
    command = user_input.strip().lower()

    if command in ('exit', 'quit'):
        return 'Exit'

    elif command.startswith('rp'):
        products = search_product_service(command)
        return format_products(products)

    elif command.startswith('ev '):
        return save_order(command)
    
    elif command.startswith('gr '):
        return return_order(command)

    elif command == 'es':
        return stock_status(command)

    elif command == 'eo':
        return orders_status(command)
    else:
        return 'Commande inconnue.'


def main():
    # Wipe la base de données au démarrage
    if prompt_reset_database():
        display_message("Réinitialisation de la base de données...")
        Base.metadata.drop_all(engine)
        Base.metadata.create_all(engine)
        display_message("Base de données réinitialisée avec succès!")
        # Initialisation de la session de base de données
        session.add_all([
            Product(name='Product 1', price=100, category='Catégorie A', stock_quantity=10),
            Product(name='Product 2', price=100, category='Catégorie A', stock_quantity=20),
        ])
    else:
        display_message("Conservation des données existantes")
    
    display_welcome_message()

    session.commit()

    analyse_input('rp')

    while True:
        try:
            user_input = prompt_command()
            response = analyse_input(user_input)
            
            if response == 'Exit':
                display_goodbye_message()
                break
            elif isinstance(response, str) and response.startswith("ID:"):
                display_products(response)
            elif isinstance(response, dict):  # Stock
                display_stock(response)
            else:
                display_message(response)
                
        except KeyboardInterrupt:
            display_goodbye_message()
            break
        except Exception as e:
            display_error(e)









if __name__ == '__main__':
    # Choix entre lancer l'API ou la CLI
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == '--api':
        run_api()
    else:
        main()  # Lancer l'interface CLI    