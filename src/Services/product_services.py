# src/Services/product_services.py
from src.DAO.product_dao import get
from src.Models.product import Product
from data.database import session

def search_product_service(search_term: str) -> str:
    # products = get(search_term)
    if search_term.isnumeric():
        search_id = int(search_term)
        all_products = get()
        products = all_products.filter(
            (Product.id == search_id) |
            (Product.name.contains(search_term)) |
            (Product.category.contains(search_term))
        ).all()
    else:
        # Si ce n'est pas un nombre, recherche seulement par nom et catégorie
        products = session.query(Product).filter(
            (Product.name.contains(search_term)) |
            (Product.category.contains(search_term))
        ).all()
    if not products:
        return "Aucun produit trouvé."
    return products

def stock_status() -> dict:
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

