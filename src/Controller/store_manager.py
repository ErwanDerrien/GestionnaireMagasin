# src/Controller/store_manager.py
from data.database import session, Product, Order, Base, engine
from src.Services.product_services import search_product, stock_status
from src.Services.order_services import save_order, return_order
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

def analyse_input(user_input: str) -> str:
    command = user_input.strip().lower()

    if command in ('exit', 'quit'):
        return 'Exit'

    elif command.startswith('rp'):
        return search_product(command)

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
    main()