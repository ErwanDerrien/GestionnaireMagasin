# src/DAO/order_dao.py
from data.database import session
from src.Models.order import Order
def query(order: Order): 
    return session.query(order)