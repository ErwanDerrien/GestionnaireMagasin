#src/services/order_services.py
from sqlalchemy import func
from sqlalchemy.exc import SQLAlchemyError
from data.database import session
from src.models.product import Product
from src.models.order import Order
from typing import List, Dict, Optional, Tuple, Union
from src.dao.order_dao import query

def save_order(order_data: Dict[str, Union[List[int], int]]) -> Dict[str, Union[str, int, List]]:
    try:
        # Validation initiale
        if not order_data or not isinstance(order_data.get('ids'), list):
            return {
                "status": "error",
                "message": "Format invalide. Utiliser {'ids': [1,2,3], 'store_id': 1}"
            }

        product_ids = order_data['ids']
        store_id = order_data.get('store_id')
        
        if not product_ids:
            return {"status": "error", "message": "Aucun produit spécifié"}
            
        if not store_id or not isinstance(store_id, int):
            return {"status": "error", "message": "Store ID manquant ou invalide"}

        # Vérification des produits
        valid_products = []
        total = 0
        errors = []

        # Transaction temporaire
        with session.begin_nested():  
            product_counts = {}
            for pid in product_ids:
                product_counts[pid] = product_counts.get(pid, 0) + 1

            seen_errors = set()
            for pid, count in product_counts.items():
                product = session.query(Product).filter(
                    Product.id == pid,
                    Product.store_id == store_id
                ).first()

                if not product:
                    msg = f"ID {pid} non trouvé dans le magasin {store_id}"
                    if msg not in seen_errors:
                        errors.append(msg)
                        seen_errors.add(msg)
                    continue

                if product.stock_quantity < count:
                    msg = f"Stock insuffisant pour: {product.name} (demande: {count}, disponible: {product.stock_quantity})"
                    if msg not in seen_errors:
                        errors.append(msg)
                        seen_errors.add(msg)
                    continue

                valid_products.extend([product] * count)
                total += product.price * count

        if errors:
            return {
                "status": "error",
                "message": "Problèmes avec certains produits",
                "errors": errors,
                "valid_products": [p.id for p in valid_products],
                "store_id": store_id
            }

        # Enregistrement final
        try:
            products_str = ",".join(str(p.id) for p in valid_products)
            
            new_order = Order(
                user_id="current_user",
                price=total,
                products=products_str,
                status="completed",
                store_id=store_id
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
                "store_id": store_id,
                "message": f"Commande #{new_order.id} enregistrée pour le magasin {store_id}"
            }
            
        except SQLAlchemyError as e:
            session.rollback()
            return {
                "status": "error",
                "message": f"Erreur base de données: {str(e)}",
                "store_id": store_id
            }
            
    except Exception as e:
        return {
            "status": "error",
            "message": f"Erreur inattendue: {str(e)}"
        }
                
def return_order(order_id: int) -> str:
    try:        
        # Vérifier la commande avant transaction
        order = query(Order).get(order_id)
        if not order:
            return f"Commande ID {order_id} non trouvée"
        
        if order.status == 'cancelled':
            return f"La commande {order_id} est déjà annulée"
        
        # Exécuter la transaction
        try:
            product_ids = order.products.split(',')
            for pid in product_ids:
                product = query(Product).get(int(pid))
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
    
def orders_status(store_id: Optional[int] = None, page: int = 1, per_page: int = 10) -> Tuple[List[Dict], Dict]:
    try:
        # Création de la requête de base
        query = session.query(Order).order_by(Order.id)

        if store_id is not None:
            query = query.filter(Order.store_id == store_id)

        # Calcul du nombre total d'éléments
        total = query.count()
        
        # Calcul du nombre de pages
        pages = (total + per_page - 1) // per_page  # Arrondi supérieur

        # Calcul de l'offset
        offset = (page - 1) * per_page
        
        # Récupération des résultats paginés
        orders = query.offset(offset).limit(per_page).all()

        # Formatage des résultats
        formatted_orders = []
        for order in orders:
            products_list = [int(pid) for pid in order.products.split(',') if pid.isdigit()]
            
            formatted_orders.append({
                "id": order.id,
                "user_id": order.user_id,
                "status": order.status,
                "products": products_list,
                "total_price": float(order.price) if order.price else 0.0,
                "store_id": order.store_id,
                # "created_at": order.created_at.isoformat() if order.created_at else None
            })

        # Construction des informations de pagination
        pagination_info = {
            "total": total,
            "pages": pages,
            "page": page,
            "per_page": per_page,
            "next": f"?page={page+1}&per_page={per_page}" if page < pages else None,
            "prev": f"?page={page-1}&per_page={per_page}" if page > 1 else None
        }

        return formatted_orders, pagination_info

    except SQLAlchemyError as e:
        raise Exception(f"Erreur de base de données: {str(e)}")
    except Exception as e:
        raise Exception(f"Erreur inattendue: {str(e)}")
    
def generate_orders_report() -> list:
    try:
        # Récupérer tous les magasins existants
        all_stores = session.query(Product.store_id).distinct().all()
        store_ids = [store[0] for store in all_stores] if all_stores else []

        # 1. Ventes par magasin avec détails par statut
        sales_by_store = []
        for store_id in store_ids:
            # Commandes complétées
            completed_orders = session.query(
                func.count(Order.id).label('count'),
                func.sum(Order.price).label('revenue')
            ).filter(
                Order.store_id == store_id,
                Order.status == 'completed'
            ).first()

            # Commandes annulées
            cancelled_orders = session.query(
                func.count(Order.id).label('count')
            ).filter(
                Order.store_id == store_id,
                Order.status == 'cancelled'
            ).first()

            sales_by_store.append({
                'store_id': store_id,
                'total_orders': (completed_orders.count or 0) + (cancelled_orders.count or 0),
                'completed_orders': completed_orders.count or 0,
                'cancelled_orders': cancelled_orders.count or 0,
                'total_revenue': float(completed_orders.revenue) if completed_orders.revenue else 0.0
            })

        # 2. Produits les plus vendus (uniquement commandes complétées)
        completed_orders = session.query(Order).filter(Order.status == 'completed').all()
        product_sales = {}
        
        for order in completed_orders:
            if order.products:
                products = order.products.split(',')
                for product_id in products:
                    if product_id.isdigit():
                        product_id = int(product_id)
                        product_sales[product_id] = product_sales.get(product_id, 0) + 1

        top_products = sorted(product_sales.items(), key=lambda x: x[1], reverse=True)[:10]
        
        top_products_details = []
        for product_id, quantity in top_products:
            product = session.get(Product, product_id)
            if product:
                top_products_details.append({
                    'product_id': product_id,
                    'name': product.name,
                    'category': product.category,
                    'quantity_sold': quantity,
                    'store_id': product.store_id
                })

        # 3. Stocks détaillés par produit et magasin
        detailed_stock = []
        for store_id in store_ids:
            products_in_store = session.query(Product).filter(Product.store_id == store_id).all()
            
            products_detail = []
            total_stock = 0
            for product in products_in_store:
                products_detail.append({
                    'product_id': product.id,
                    'name': product.name,
                    'stock': product.stock_quantity,
                    'category': product.category
                })
                total_stock += product.stock_quantity

            detailed_stock.append({
                'store_id': store_id,
                'total_stock': total_stock,
                'product_count': len(products_in_store),
                'stock_status': 'OK' if total_stock > 10 else 'LOW',
                'products_detail': products_detail
            })

        # Formatage final
        report = {
            'sales_by_store': sales_by_store,
            'top_products': top_products_details,
            'remaining_stock': detailed_stock,
            'all_store_ids': store_ids  # Pour référence
        }

        return [report]
    
    except SQLAlchemyError as e:
        print(f"Erreur SQL: {str(e)}")
        return []
    except Exception as e:
        print(f"Erreur inattendue: {str(e)}")
        return []