# src/dao/product_dao.py
from data.database import session
from src.models.product import Product
def query(product: Product): 
    return session.query(product)
