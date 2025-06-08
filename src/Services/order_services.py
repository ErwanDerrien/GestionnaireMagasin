#src/Services/order_services.py
import datetime
from data.database import session
from src.Models.product import Product
from src.Models.order import Order
from src.Views.console_view import format_orders
from typing import List, Dict, Union

from typing import List, Dict, Union
from datetime import datetime
from sqlalchemy.exc import SQLAlchemyError

def save_order(order_data: Dict[str, List[int]]) -> Dict[str, Union[str, int, List]]:
    try:
        # Validation initiale
        if not order_data or not isinstance(order_data.get('ids'), list):
            return {
                "status": "error",
                "message": "Format invalide. Utiliser {'ids': [1,2,3]}"
            }

        product_ids = order_data['ids']
        if not product_ids:
            return {"status": "error", "message": "Aucun produit spécifié"}

        # Vérification des produits
        valid_products = []
        total = 0
        errors = []

        with session.begin_nested():  # Transaction temporaire
            for pid in product_ids:
                product = session.get(Product, pid)
                if not product:
                    errors.append(f"ID {pid} non trouvé")
                elif product.stock_quantity < 1:
                    errors.append(f"Stock épuisé: {product.name}")
                else:
                    valid_products.append(product)
                    total += product.price

        if errors:
            return {
                "status": "error",
                "message": "Problèmes avec certains produits",
                "errors": errors,
                "valid_products": [p.id for p in valid_products]
            }

        # Enregistrement final
        try:
            products_str = ",".join(str(p.id) for p in valid_products)
            
            new_order = Order(
                user_id="current_user",
                price=total,
                products=products_str,
                status="completed",
            )
            
            # Mise à jour du stock
            for p in valid_products:
                p.stock_quantity -= 1
                session.add(p)
            
            session.add(new_order)
            session.commit()
            
            return {
                "status": "success",
                "order_id": new_order.id,
                "total": total,
                "products": products_str,
                "message": f"Commande #{new_order.id} enregistrée"
            }
            
        except SQLAlchemyError as e:
            session.rollback()
            return {
                "status": "error",
                "message": f"Erreur base de données: {str(e)}"
            }
            
    except Exception as e:
        return {
            "status": "error",
            "message": f"Erreur inattendue: {str(e)}"
        }
                
def return_order(order_id: int) -> str:
    try:        
        # Vérifier la commande avant transaction
        order = session.query(Order).get(order_id)
        if not order:
            return f"Commande ID {order_id} non trouvée"
        
        if order.status == 'cancelled':
            return f"La commande {order_id} est déjà annulée"
        
        # Exécuter la transaction
        try:
            product_ids = order.products.split(',')
            for pid in product_ids:
                product = session.query(Product).get(int(pid))
                if product:
                    product.stock_quantity += 1
            
            order.status = 'cancelled'
            session.commit()
            
            return f"Commande {order_id} annulée avec succès. Stock mis à jour."
        
        except Exception as e:
            session.rollback()
            return f"Erreur lors de l'annulation: {str(e)}"
            
    except ValueError:
        return "Format invalide. Utilisez: gr id_commande"
    except Exception as e:
        return f"Erreur: {str(e)}"
    
def orders_status() -> List[Dict]:
    try:
        all_orders = session.query(Order).order_by(Order.id).all()
        
        if not all_orders:
            return []
        
        formatted_orders = []
        for order in all_orders:
            # Convertit la string "1,2,3" en [1, 2, 3]
            products_list = [int(pid) for pid in order.products.split(',') if pid.isdigit()]
            
            formatted_orders.append({
                "id": order.id,
                "user_id": order.user_id,
                "status": order.status,
                "products": products_list,
                "total_price": float(order.price) if order.price else 0.0
            })
        
        return formatted_orders
        
    except Exception as e:
        raise Exception(f"Erreur lors du formatage des commandes: {str(e)}")