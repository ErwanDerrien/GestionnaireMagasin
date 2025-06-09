# src/Services/product_services.py
from data.database import apply_restock_logic
from src.Models.product import Product
from src.DAO.product_dao import query

def search_product_service(search_term: str) -> list:
    try:
        if search_term.isnumeric():
            search_id = int(search_term)
            products = query(Product).filter(
                (Product.id == search_id) |
                (Product.name.contains(search_term)) |
                (Product.category.contains(search_term))
            ).all()
        else:
            products = query(Product).filter(
                (Product.name.contains(search_term)) |
                (Product.category.contains(search_term))
            ).all()
            
        return products if products else []
        
    except Exception as e:
        print(f"Erreur lors de la recherche: {str(e)}")
        return []

def stock_status(store_id=None):
    query_builder = query(Product).order_by(Product.id)

    if store_id is not None:
        query_builder = query_builder.filter(Product.store_id == store_id)

    products = query_builder.all()

    return [{
        'id': p.id,
        'name': p.name,
        'category': p.category,
        'price': p.price,
        'stock_quantity': p.stock_quantity,
        'store_id': p.store_id
    } for p in products] if products else []

def restock_store_products(store_id: int) -> dict:
    if not (1 <= store_id <= 5):
        return {
            "success": False,
            "details": [f"Store ID invalide : {store_id}"]
        }

    return apply_restock_logic(store_id)

