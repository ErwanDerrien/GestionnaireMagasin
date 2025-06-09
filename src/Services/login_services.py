def login(username: str, password: str, store_id: int) -> dict:
    if store_id not in [0, 1, 2, 3, 4, 5]:
        return {"success": False, "error": "Invalid store ID", "status_code": 400}

    if username == "manager":
        if store_id != 0:
            return {"success": False, "error": "Le gestionnaire doit utiliser le magasin 0", "status_code": 400}
        if password == "test":
            return {"success": True, "status": "manager"}
        else:
            return {"success": False, "error": "Invalid credentials", "status_code": 401}

    elif username == "employee":
        if store_id == 0:
            return {"success": False, "error": "L'employe ne peut pas utiliser le magasin 0", "status_code": 400}
        if password == "test":
            return {"success": True, "status": "employee"}
        else:
            return {"success": False, "error": "Invalid credentials", "status_code": 401}

    return {"success": False, "error": "Invalid credentials", "status_code": 401}
