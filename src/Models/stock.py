from dataclasses import dataclass
from Models.product import Product

@dataclass
class Inventory:
    products: list['Product']