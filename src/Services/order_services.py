#src/Services/order_services.py
from data.database import session
from src.Models.product import Product
from src.Models.order import Order
from src.Views.console_view import format_orders
def save_order(command: str) -> str :
    try:
        # Extraire les IDs des produits
        product_ids = [int(id_str.strip()) for id_str in command[3:].split(',')]
        
        # Vérifier les produits avant de commencer la transaction
        products = []
        total_price = 0
        errors = []
        
        for product_id in product_ids:
            product = session.get(Product, product_id)
            if not product:
                errors.append(f"Produit ID {product_id} non trouvé")
            elif product.stock_quantity < 1:
                errors.append(f"Stock insuffisant pour {product.name}")
            else:
                products.append(product)
                total_price += product.price
        
        if errors:
            return "\n".join(errors)
        
        # Confirmation utilisateur
        print(f"Produits à commander:")
        for p in products:
            print(f"- {p.name}: {p.price}$")
        print(f"Total: {total_price}$")
        
        if input("Confirmer la commande? (o/n) ").lower() != 'o':
            return "Commande annulée"
        
        # Exécuter la transaction
        try:
            for p in products:
                p.stock_quantity -= 1
            
            new_order = Order(
                user_id="current_user",
                price=total_price,
                products=",".join(str(p.id) for p in products),
                status="completed"
            )
            session.add(new_order)
            session.commit()
            
            return (f"Commande #{new_order.id} enregistrée!\n"
                    f"Total: {total_price}$\n"
                    f"Produits: {', '.join(p.name for p in products)}")
        
        except Exception as e:
            session.rollback()
            return f"Erreur lors de la commande: {str(e)}"
            
    except ValueError:
        return "Format invalide. Utilisez: ev id1,id2,id3"
    except Exception as e:
        return f"Erreur: {str(e)}"

def return_order(command: str) -> str:
    try:
        order_id = int(command[3:].strip())
        
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
    
def orders_status(command: str) -> str:
    all_orders = session.query(Order).order_by(Order.id).all()
    if not all_orders:
        return None
    return format_orders(all_orders, session)