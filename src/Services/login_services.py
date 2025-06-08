def login(username: str, password: str) -> bool:
    if username == "manager":
        return True
    
    if username == "worker":
        return True
    
    return False