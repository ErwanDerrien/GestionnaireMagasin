# src/dao/order_dao.py
from data.database import session
from src.models.order import Order
def query(order: Order): 
    return session.query(order)