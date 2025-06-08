from sqlalchemy import Column, Integer, String
from data.database import Base

class Product(Base):
    __tablename__ = 'products'
    
    id = Column(Integer, primary_key=True)
    name = Column(String)
    price = Column(Integer)  # Note: Vous utilisez Integer pour le prix
    category = Column(String)
    stock_quantity = Column(Integer)
    
    def to_dict(self):
        """Convertit l'objet Product en dictionnaire sérialisable"""
        return {
            'id': self.id,
            'name': self.name,
            'price': self.price,  # Pas besoin de conversion si c'est déjà un Integer
            'category': self.category,
            'stock_quantity': self.stock_quantity
        }