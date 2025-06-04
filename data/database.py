from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from pathlib import Path
import os

# Base de données
Base = declarative_base()

# Définition des modèles
class Product(Base):
    __tablename__ = 'products'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    price = Column(Integer)
    category = Column(String)
    stock_quantity = Column(Integer)

class Order(Base):
    __tablename__ = 'orders'
    id = Column(Integer, primary_key=True)
    user_id = Column(String)
    price = Column(Integer)
    products = Column(String)
    status = Column(String)

# Chemin vers la base de données dans le dossier data
DB_PATH = Path(__file__).parent / "mydatabase.db"

# Moteur SQLite
engine = create_engine(f'sqlite:///{DB_PATH}', echo=False)

# Création des tables
Base.metadata.create_all(engine)

# Session pour interagir avec la base
Session = sessionmaker(bind=engine)
session = Session()