def login(username: str, password: str, store_id: int) -> dict:
    """
    Authentifie un utilisateur selon son rôle et magasin assigné.
    
    Args:
        username: Nom d'utilisateur ("manager" ou "employee")
        password: Mot de passe de l'utilisateur
        store_id: ID du magasin (0-5, où 0 = siège social)
    
    Returns:
        dict: Résultat de l'authentification avec success, status/error, status_code
    """
    # Validation des paramètres d'entrée
    if not isinstance(username, str) or not username.strip():
        return {"success": False, "error": "Nom d'utilisateur invalide", "status_code": 400}
    
    if not isinstance(password, str) or not password.strip():
        return {"success": False, "error": "Mot de passe invalide", "status_code": 400}
    
    if not isinstance(store_id, int) or store_id not in range(6):  # 0-5
        return {"success": False, "error": "ID de magasin invalide (doit être entre 0 et 5)", "status_code": 400}
    
    # Normalisation de l'entrée
    username = username.strip().lower()
    password = password.strip()
    
    # Authentification selon le rôle
    if username == "manager":
        return _authenticate_manager(password, store_id)
    elif username == "employee":
        return _authenticate_employee(password, store_id)
    else:
        return {"success": False, "error": "Utilisateur non reconnu", "status_code": 401}


def _authenticate_manager(password: str, store_id: int) -> dict:
    """Authentifie un gestionnaire."""
    if store_id != 0:
        return {
            "success": False, 
            "error": "Le gestionnaire doit utiliser le magasin 0 (siège social)", 
            "status_code": 403
        }
    
    if password != "test":
        return {"success": False, "error": "Mot de passe incorrect", "status_code": 401}
    
    return {
        "success": True, 
        "role": "manager",  # Changé de "status" à "role"
        "store_id": store_id,
        "permissions": ["read", "write", "admin"],
        "status_code": 200
    }


def _authenticate_employee(password: str, store_id: int) -> dict:
    """Authentifie un employé."""
    if store_id == 0:
        return {
            "success": False, 
            "error": "L'employé ne peut pas accéder au siège social (magasin 0)", 
            "status_code": 403
        }
    
    if password != "test":
        return {"success": False, "error": "Mot de passe incorrect", "status_code": 401}
    
    return {
        "success": True, 
        "role": "employee",  # Changé de "status" à "role"
        "store_id": store_id,
        "permissions": ["read", "write"],
        "status_code": 200
    }


# Exemple d'utilisation et tests
if __name__ == "__main__":
    # Tests de validation
    test_cases = [
        # Cas valides
        ("manager", "test", 0),
        ("employee", "test", 1),
        ("employee", "test", 5),
        
        # Cas invalides
        ("manager", "test", 1),      # Manager sur mauvais magasin
        ("employee", "test", 0),     # Employé sur siège social
        ("manager", "wrong", 0),     # Mauvais mot de passe
        ("employee", "wrong", 1),    # Mauvais mot de passe
        ("admin", "test", 1),        # Utilisateur inexistant
        ("", "test", 1),             # Username vide
        ("manager", "", 0),          # Mot de passe vide
        ("manager", "test", 6),      # Store ID invalide
    ]
    
    for username, password, store_id in test_cases:
        result = login(username, password, store_id)
        print(f"login('{username}', '{password}', {store_id}) -> {result}")