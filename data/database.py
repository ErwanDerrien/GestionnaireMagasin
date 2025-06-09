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
            Product(name='Product 1', price=100, category='Catégorie A', stock_quantity=10, store_id=1),
            Product(name='Product 2', price=100, category='Catégorie A', stock_quantity=20, store_id=1),
            Product(name='Product 1', price=100, category='Catégorie A', stock_quantity=10, store_id=2),
            Product(name='Product 2', price=100, category='Catégorie A', stock_quantity=20, store_id=2),
            Product(name='Troisieme prod', price=100, category='Catégorie B', stock_quantity=30, store_id=2),
            Product(name='Product 1', price=100, category='Catégorie A', stock_quantity=10, store_id=3),
            Product(name='Product 2', price=100, category='Catégorie A', stock_quantity=20, store_id=3),
            Product(name='Troisieme prod', price=100, category='Catégorie B', stock_quantity=30, store_id=3),
            Product(name='Quatrième prod', price=100, category='Catégorie B', stock_quantity=30, store_id=3),
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
        

def reset_store_products(store_id: int, products: list[Product]) -> bool:
    try:
        session.query(Product).filter_by(store_id=store_id).delete()
        session.add_all(products)
        session.commit()
        return True

    except Exception as e:
        session.rollback()
        print(f"Erreur lors du reset des produits du magasin {store_id} : {str(e)}")
        return False

    finally:
        session.close()
