from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from pathlib import Path

# Configuration existante
Base = declarative_base()
DB_PATH = Path(__file__).parent / "mydatabase.db"
engine = create_engine(f'sqlite:///{DB_PATH}', echo=False)
Session = sessionmaker(bind=engine)
session = Session()

from src.Models.order import Order
from src.Models.product import Product

def reset_database() -> bool:
    try:
        # Suppression et recréation des tables
        Base.metadata.drop_all(engine)
        Base.metadata.create_all(engine)
        
        # Préparation des données initiales
        initial_products = [
            Product(name='Product 1', price=100, category='Catégorie A', stock_quantity=1000, store_id=0),
            Product(name='Product 2', price=100, category='Catégorie A', stock_quantity=1000, store_id=0),
            Product(name='Troisieme prod', price=100, category='Catégorie B', stock_quantity=2000, store_id=0),
            Product(name='Quatrième prod', price=100, category='Catégorie B', stock_quantity=2000, store_id=0),
            Product(name='Product 1', price=100, category='Catégorie A', stock_quantity=10, store_id=1, max_quantity=50),
            Product(name='Product 2', price=100, category='Catégorie A', stock_quantity=20, store_id=1, max_quantity=50),
            Product(name='Product 1', price=100, category='Catégorie A', stock_quantity=10, store_id=2, max_quantity=50),
            Product(name='Product 2', price=100, category='Catégorie A', stock_quantity=20, store_id=2, max_quantity=50),
            Product(name='Troisieme prod', price=100, category='Catégorie B', stock_quantity=30, store_id=2, max_quantity=50),
            Product(name='Product 1', price=100, category='Catégorie A', stock_quantity=10, store_id=3, max_quantity=50),
            Product(name='Product 2', price=100, category='Catégorie A', stock_quantity=20, store_id=3, max_quantity=50),
            Product(name='Troisieme prod', price=100, category='Catégorie B', stock_quantity=30, store_id=3, max_quantity=50),
            Product(name='Quatrième prod', price=100, category='Catégorie B', stock_quantity=30, store_id=3, max_quantity=50),
        ]
        
        # Conversion des produits en string pour la commande
        products_str = ",".join(map(str, [1, 1, 2]))
        
        # Ajout des données initiales
        session.add(Order(user_id='current_user', price=300, products=products_str, status='completed', store_id=1))
        session.add_all(initial_products)
        session.commit()
        
        return True
        
    except Exception as e:
        session.rollback()
        print(f"Erreur lors de la réinitialisation de la base de données: {str(e)}")
        return False
    finally:
        session.close()
        
def apply_restock_logic(store_id: int) -> dict:
    details = []

    try:
        store_products = session.query(Product).filter_by(store_id=store_id).all()

        for store_product in store_products:
            product_name = store_product.name

            # Rechercher le produit équivalent dans le stock central
            central_product = session.query(Product).filter_by(
                store_id=0,
                name=store_product.name,
                category=store_product.category,
                price=store_product.price
            ).with_for_update().first()  # verrouille pour éviter les conflits

            if not central_product:
                details.append({
                    "product": product_name,
                    "status": "introuvable dans le stock central"
                })
                continue

            missing_quantity = store_product.max_quantity - store_product.stock_quantity
            if missing_quantity <= 0:
                details.append({
                    "product": product_name,
                    "status": "déjà plein"
                })
                continue

            if central_product.stock_quantity <= 0:
                details.append({
                    "product": product_name,
                    "status": "stock central vide"
                })
                continue

            # Quantité à transférer
            transfer_quantity = min(missing_quantity, central_product.stock_quantity)

            # Mise à jour des quantités
            store_product.stock_quantity += transfer_quantity
            central_product.stock_quantity -= transfer_quantity

            # Comme les objets sont liés à la session, ces changements seront pris en compte au commit
            details.append({
                "product": product_name,
                "status": f"rempli de {transfer_quantity} unités"
            })

        session.commit()
        return {
            "success": True,
            "details": details
        }

    except Exception as e:
        session.rollback()
        return {
            "success": False,
            "details": [f"Erreur BD : {str(e)}"]
        }
