from sqlalchemy import Column, Integer, String
from data.database import Base

class Product(Base):
    __tablename__ = 'products'
    
    id = Column(Integer, primary_key=True)
    name = Column(String)
    price = Column(Integer)
    category = Column(String)
    stock_quantity = Column(Integer)
    store_id = Column(Integer)
    max_quantity = Column(Integer)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'price': self.price,
            'category': self.category,
            'stock_quantity': self.stock_quantity,
            'store_id': self.store_id,
            'max_quantity': self.max_quantity,
        }