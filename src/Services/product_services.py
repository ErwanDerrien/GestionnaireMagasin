# src/Services/product_services.py
from data.database import session, Product, Order, Base, engine
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
def search_product(command: str) -> str:
    """
    Recherche des produits en fonction d'un terme
    """
    search_term = command[3:].strip()
    try:
        search_id = int(search_term)
        products = session.query(Product).filter(
            (Product.id == search_id) |
            (Product.name.contains(search_term)) |
            (Product.category.contains(search_term))
        ).all()
    except ValueError:
        # Si ce n'est pas un nombre, recherche seulement par nom et catégorie
        products = session.query(Product).filter(
            (Product.name.contains(search_term)) |
            (Product.category.contains(search_term))
        ).all()
    
    if not products:
        return "Aucun produit trouvé."
    
    # Retourne les résultats formatés
    return format_products(products)

def stock_status(command: str) -> dict:
    all_products = session.query(Product).order_by(Product.id).all()
    if not all_products:
        return None  # Sera géré par l'affichage comme "Aucun produit en base"
    
    # Créer un dictionnaire avec toutes les infos nécessaires
    products_info = {
        p.name: {
            'id': p.id,
            'category': p.category,
            'price': p.price,
            'stock': p.stock_quantity
        } 
        for p in all_products
    }
    return products_info

