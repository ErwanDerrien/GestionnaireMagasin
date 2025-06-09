# src/Services/product_services.py
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

def stock_status():
    all_products = query(Product).order_by(Product.id).all()
    
    return [{
        'id': p.id,
        'name': p.name,
        'category': p.category,
        'price': p.price,
        'stock_quantity': p.stock_quantity,
        'store_id': p.store_id
    } for p in all_products] if all_products else []

