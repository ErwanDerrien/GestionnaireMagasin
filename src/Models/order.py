from sqlalchemy import Column, Integer, String
from data.database import Base
class Order(Base):
    __tablename__ = 'orders'
    id = Column(Integer, primary_key=True)
    user_id = Column(String)
    price = Column(Integer)
    products = Column(String)
    status = Column(String)