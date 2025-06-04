from dataclasses import dataclass

@dataclass
class Product:
    id: str
    name: str
    price: float
    category: str
    stock_quantity: int