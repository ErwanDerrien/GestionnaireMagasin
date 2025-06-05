from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from pathlib import Path

# Base de données
Base = declarative_base()

# Chemin vers la base de données dans le dossier data
DB_PATH = Path(__file__).parent / "mydatabase.db"

# Moteur SQLite
engine = create_engine(f'sqlite:///{DB_PATH}', echo=False)

# Création des tables
Base.metadata.create_all(engine)

# Session pour interagir avec la base
Session = sessionmaker(bind=engine)
session = Session()