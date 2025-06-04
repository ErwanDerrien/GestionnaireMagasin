from dataclasses import dataclass

@dataclass
class Order:
    id: str
    user_id: str
    price: float
    products: list[str]
    status: str