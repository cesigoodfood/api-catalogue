from django.core.management.base import BaseCommand
from catalogue.models import Product, Category, Menu, ProductCategory

class Command(BaseCommand):
    help = 'Seeds the catalogue database with mock data for restaurants'

    def handle(self, *args, **kwargs):
        self.stdout.write('Seeding catalogue... clearing old data...')

        ProductCategory.objects.all().delete()
        Product.objects.all().delete()
        Category.objects.all().delete()
        Menu.objects.all().delete()

        # Restaurant 1: Pizza Paradise
        # Categories
        cat_pizzas = Category.objects.create(restaurant_id=1, name='Pizzas')
        cat_desserts = Category.objects.create(restaurant_id=1, name='Desserts')

        # Products
        p1 = Product.objects.create(restaurant_id=1, name='Pizza Margherita', description='Tomate, mozzarella, basilic frais', price=12.5, image_url='/menu/pizza-margherita.jpg', category=cat_pizzas)
        p2 = Product.objects.create(restaurant_id=1, name='Pizza 4 Fromages', description='Mozzarella, gorgonzola, parmesan, chèvre', price=14.9, image_url='/menu/pizza-4fromages.jpg', category=cat_pizzas)
        p3 = Product.objects.create(restaurant_id=1, name='Pizza Pepperoni', description='Tomate, mozzarella, pepperoni épicé', price=13.5, image_url='/menu/pizza-pepperoni.jpg', category=cat_pizzas)
        p4 = Product.objects.create(restaurant_id=1, name='Tiramisu', description='Dessert italien traditionnel', price=6.5, image_url='/menu/tiramisu.jpg', category=cat_desserts)

        ProductCategory.objects.create(product=p1, category=cat_pizzas)
        ProductCategory.objects.create(product=p2, category=cat_pizzas)
        ProductCategory.objects.create(product=p3, category=cat_pizzas)
        ProductCategory.objects.create(product=p4, category=cat_desserts)

        # Restaurant 2: Burger King Supreme
        cat_burgers = Category.objects.create(restaurant_id=2, name='Burgers')
        cat_sides = Category.objects.create(restaurant_id=2, name='Accompagnements')

        p1_2 = Product.objects.create(restaurant_id=2, name='Classic Burger', description='Steak haché, salade, tomate, oignon, sauce maison', price=11.9, image_url='/menu/classic-burger.jpg', category=cat_burgers)
        p2_2 = Product.objects.create(restaurant_id=2, name='Bacon Cheese Burger', description='Double steak, bacon croustillant, cheddar fondu', price=14.5, image_url='/menu/bacon-burger.jpg', category=cat_burgers)
        p3_2 = Product.objects.create(restaurant_id=2, name='Veggie Burger', description='Steak végétarien, avocat, légumes grillés', price=12.9, image_url='/menu/veggie-burger.jpg', category=cat_burgers)
        p4_2 = Product.objects.create(restaurant_id=2, name='Frites Maison', description='Frites croustillantes avec sauce au choix', price=4.5, image_url='/menu/fries.jpg', category=cat_sides)

        ProductCategory.objects.create(product=p1_2, category=cat_burgers)
        ProductCategory.objects.create(product=p2_2, category=cat_burgers)
        ProductCategory.objects.create(product=p3_2, category=cat_burgers)
        ProductCategory.objects.create(product=p4_2, category=cat_sides)

        # Restaurant 3: Sushi Master
        cat_sushis = Category.objects.create(restaurant_id=3, name='Sushis')
        cat_makis = Category.objects.create(restaurant_id=3, name='Makis')
        cat_sashimis = Category.objects.create(restaurant_id=3, name='Sashimis')

        p1_3 = Product.objects.create(restaurant_id=3, name='Sushi Mix 12 pièces', description='Assortiment de sushis et makis', price=18.9, image_url='/menu/sushi-mix.jpg', category=cat_sushis)
        p2_3 = Product.objects.create(restaurant_id=3, name='California Roll', description='Surimi, avocat, concombre, tobiko', price=8.5, image_url='/menu/california.jpg', category=cat_makis)
        p3_3 = Product.objects.create(restaurant_id=3, name='Sashimi Saumon', description='8 tranches de saumon frais', price=15.9, image_url='/menu/sashimi.jpg', category=cat_sashimis)
        
        ProductCategory.objects.create(product=p1_3, category=cat_sushis)
        ProductCategory.objects.create(product=p2_3, category=cat_makis)
        ProductCategory.objects.create(product=p3_3, category=cat_sashimis)

        self.stdout.write(self.style.SUCCESS('Successfully seeded catalogue database.'))
