# src/Services/product_services.py
from data.database import reset_store_products
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

def restock_store_products(store_id: int) -> bool:
    # Définition des produits à ajouter selon le magasin
    store_products_map = {
        1: [
            Product(name='Product 1', price=100, category='Catégorie A', stock_quantity=10, store_id=1),
            Product(name='Product 2', price=100, category='Catégorie A', stock_quantity=20, store_id=1),
        ],
        2: [
            Product(name='Product 1', price=100, category='Catégorie A', stock_quantity=10, store_id=2),
            Product(name='Product 2', price=100, category='Catégorie A', stock_quantity=20, store_id=2),
            Product(name='Troisieme prod', price=100, category='Catégorie B', stock_quantity=30, store_id=2),
        ],
        3: [
            Product(name='Product 1', price=100, category='Catégorie A', stock_quantity=10, store_id=3),
            Product(name='Product 2', price=100, category='Catégorie A', stock_quantity=20, store_id=3),
            Product(name='Troisieme prod', price=100, category='Catégorie B', stock_quantity=30, store_id=3),
            Product(name='Quatrième prod', price=100, category='Catégorie B', stock_quantity=30, store_id=3),
        ]
    }

    products_to_add = store_products_map.get(store_id, [])
    return reset_store_products(store_id, products_to_add)
