# src/DAO/product_dao.py
from data.database import session
from src.Models.product import Product
def query(product: Product): 
    return session.query(product)
