# src/services/product_services.py
from data.database import apply_restock_logic, session
from src.models.product import Product
from src.dao.product_dao import query
from typing import Tuple, List, Dict, Optional

def search_product_service(search_term: str, page: int = 1, per_page: int = 10) -> Tuple[List[Dict], Dict]:
    try:
        query = session.query(Product)
        
        if search_term.isnumeric():
            search_id = int(search_term)
            query = query.filter(
                (Product.id == search_id) |
                (Product.name.contains(search_term)) |
                (Product.category.contains(search_term))
            )
        else:
            query = query.filter(
                (Product.name.contains(search_term)) |
                (Product.category.contains(search_term))
            )
        
        # Pagination manuelle
        total = query.count()
        pages = (total + per_page - 1) // per_page
        
        offset = (page - 1) * per_page
        products = query.offset(offset).limit(per_page).all()
            
        serialized_products = [{
            'id': p.id,
            'name': p.name,
            'category': p.category,
            'price': p.price,
            'stock_quantity': p.stock_quantity,
            'store_id': p.store_id
        } for p in products]
        
        pagination_info = {
            'total': total,
            'pages': pages,
            'page': page,
            'per_page': per_page,
            'next': f"?page={page+1}&per_page={per_page}" if page < pages else None,
            'prev': f"?page={page-1}&per_page={per_page}" if page > 1 else None
        }
        
        return serialized_products, pagination_info
        
    except Exception as e:
        print(f"Erreur lors de la recherche: {str(e)}")
        return [], {}

def stock_status(store_id: Optional[int] = None, page: int = 1, per_page: int = 10) -> Tuple[List[Dict], Dict]:
    try:
        query = session.query(Product).order_by(Product.id)

        if store_id is not None:
            query = query.filter(Product.store_id == store_id)

        # Implémentation manuelle de la pagination
        total = query.count()
        pages = (total + per_page - 1) // per_page  # Calcul du nombre de pages
        
        # Récupération des résultats paginés
        offset = (page - 1) * per_page
        products = query.offset(offset).limit(per_page).all()

        formatted_products = [{
            'id': p.id,
            'name': p.name,
            'category': p.category,
            'price': p.price,
            'stock_quantity': p.stock_quantity,
            'store_id': p.store_id
        } for p in products]

        pagination_info = {
            'total': total,
            'pages': pages,
            'page': page,
            'per_page': per_page,
            'next': f"?page={page+1}&per_page={per_page}" if page < pages else None,
            'prev': f"?page={page-1}&per_page={per_page}" if page > 1 else None
        }

        return formatted_products, pagination_info

    except Exception as e:
        raise Exception(f"Erreur lors de la récupération du stock: {str(e)}")

def restock_store_products(store_id: int) -> dict:
    if not (1 <= store_id <= 5):
        return {
            "success": False,
            "details": [f"Store ID invalide : {store_id}"]
        }

    return apply_restock_logic(store_id)

