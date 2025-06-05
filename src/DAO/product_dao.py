# src/DAO/product_dao.py
from data.database import session
from src.Models.product import Product
def get(): 
    return session.query(Product)
