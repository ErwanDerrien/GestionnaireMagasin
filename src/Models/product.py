from sqlalchemy import Column, Integer, String
from data.database import Base
class Product(Base):
    __tablename__ = 'products'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    price = Column(Integer)
    category = Column(String)
    stock_quantity = Column(Integer)