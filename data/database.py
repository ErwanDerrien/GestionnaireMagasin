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

from src.Models.product import Product

def reset_database() -> bool:
    try:
        Base.metadata.drop_all(engine)
        Base.metadata.create_all(engine)
        
        initial_products = [
            Product(name='Product 1', price=100, category='Catégorie A', stock_quantity=10),
            Product(name='Product 2', price=100, category='Catégorie A', stock_quantity=20),
        ]
        
        session.add_all(initial_products)
        session.commit()
        return True
        
    except Exception:
        session.rollback()
        return False
    finally:
        session.close()