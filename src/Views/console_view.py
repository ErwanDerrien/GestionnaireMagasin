# src/Views/console_view.py
from src.Models.product import Product
def display_welcome_message():
    print('\nBienvenue dans le gestionnaire de magasin !')
    print('Entrez "exit" ou "quit" pour quitter.')
    print('Commandes :')
    print('rp (rechercher un produit)')
    print('ev id1,id2 (enregistrer une vente)')
    print('gr id (annuler une commande)')
    print('es (état des stocks)')
    print('eo (état des commandes)')
    
def display_goodbye_message():
    print('Au revoir !')

def display_error(error: Exception):
    print(f'Erreur: {error}')

def display_stock(stock_data):
    if not stock_data:
        print("Aucun produit en base.")
    else:
        # En-tête du tableau
        print("\nÉtat des stocks:")
        print(f"{'ID':<5} | {'Nom':<20} | {'Catégorie':<20} | {'Prix':<8} | {'Stock'}")
        print("-" * 70)
        
        # Lignes de produits
        for name, info in stock_data.items():
            print(
                f"{info['id']:<5} | {name:<20} | {info['category']:<20} | "
                f"{info['price']:<8} | {info['stock']}"
            )

def display_message(message: str):
    print(message)

def prompt_reset_database():
    return input("Voulez-vous réinitialiser la base de données? (y/n) ").lower() == 'y'

def prompt_command():
    return input('> ').strip()

def display_products(products_list):
    if not products_list:
        print("Aucun produit trouvé.")
    else:
        print("\nRésultats de la recherche:")
        print(products_list)
        
def format_products(products):
    # Définir les largeurs de colonnes
    col_widths = {
        'id': 5,
        'name': 20,
        'category': 20,
        'price': 8,
        'stock': 5
    }
    
    # Créer le format dynamiquement
    fmt = (
        f"{{id:<{col_widths['id']}}} | {{name:<{col_widths['name']}}} | "
        f"{{category:<{col_widths['category']}}} | {{price:<{col_widths['price']}}} | "
        f"{{stock:<{col_widths['stock']}}}"
    )
    
    # En-tête
    header = fmt.format(
        id='ID',
        name='Nom',
        category='Catégorie',
        price='Prix$',
        stock='Stock'
    )
    separator = '-' * len(header)
    
    # Lignes
    rows = []
    for p in products:
        rows.append(fmt.format(
            id=p.id,
            name=p.name[:col_widths['name']],
            category=p.category[:col_widths['category']],
            price=f"{p.price}$",
            stock=p.stock_quantity
        ))
    
    return '\n'.join([header, separator, *rows])

def display_orders(orders_list):
    print("\nListe des commandes:")
    print(orders_list)

def format_orders(orders, session):
    # Définir les largeurs de colonnes
    col_widths = {
        'id': 5,
        'user_id': 15,
        'products': 40,  # Augmenté pour accommoder les noms
        'price': 10,
        'status': 15
    }
    
    # Créer le format dynamiquement
    fmt = (
        f"{{id:<{col_widths['id']}}} | {{user_id:<{col_widths['user_id']}}} | "
        f"{{products:<{col_widths['products']}}} | {{price:<{col_widths['price']}}} | "
        f"{{status:<{col_widths['status']}}}"
    )
    
    # En-tête
    header = fmt.format(
        id='ID',
        user_id='Utilisateur',
        products='Produits',
        price='Prix',
        status='Statut'
    )
    separator = '-' * len(header)
    
    # Lignes
    rows = []
    for order in orders:
        # Convertir les IDs en noms de produits
        product_ids = order.products.split(',')
        products = []
        for pid in product_ids:
            product = session.query(Product).get(int(pid))
            if product:
                products.append(product.name)
        
        rows.append(fmt.format(
            id=order.id,
            user_id=order.user_id[:col_widths['user_id']],
            products=", ".join(products)[:col_widths['products']],
            price=f"{order.price}$",
            status=order.status[:col_widths['status']]
        ))
    
    return '\n'.join([header, separator, *rows])
