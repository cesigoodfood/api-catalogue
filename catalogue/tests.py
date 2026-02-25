from unittest.mock import Mock, patch

from django.contrib.auth import get_user_model
from django.db import connections
from django.test import TestCase
from django.test import override_settings
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from .models import (
    Category,
    CategoryMenu,
    Menu,
    Product,
    ProductCategory,
    ProductCategoryMenu,
)


@override_settings(STOCK_API_BASE="http://stock.test/api")
class CatalogueRoutesTests(APITestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.publish_event_patcher = patch("catalogue.signals.publish_catalogue_event")
        cls.publish_event_patcher.start()

    @classmethod
    def tearDownClass(cls):
        cls.publish_event_patcher.stop()
        super().tearDownClass()

    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="tester",
            password="testpass123",
        )

        self.category_r1 = Category.objects.create(
            restaurant_id=1,
            name="Burgers",
            description="Cat r1",
        )
        self.category_r2 = Category.objects.create(
            restaurant_id=2,
            name="Desserts",
            description="Cat r2",
        )

        self.menu_r1 = Menu.objects.create(
            restaurant_id=1,
            name="Midi",
            description="Menu r1",
            price="12.50",
        )
        self.menu_r2 = Menu.objects.create(
            restaurant_id=2,
            name="Soir",
            description="Menu r2",
            price="18.90",
        )

        self.product_r1 = Product.objects.create(
            restaurant_id=1,
            name="Cheeseburger",
            description="Produit r1",
            price="10.00",
            category=self.category_r1,
        )
        self.product_r2 = Product.objects.create(
            restaurant_id=2,
            name="Tiramisu",
            description="Produit r2",
            price="6.00",
            category=self.category_r2,
        )

        self.menu_category_r1 = CategoryMenu.objects.create(
            menu=self.menu_r1,
            name="Plats",
            quantity=1,
        )
        self.menu_category_r2 = CategoryMenu.objects.create(
            menu=self.menu_r2,
            name="Desserts",
            quantity=1,
        )

        ProductCategoryMenu.objects.create(
            category=self.menu_category_r1,
            product=self.product_r1,
        )
        ProductCategoryMenu.objects.create(
            category=self.menu_category_r2,
            product=self.product_r2,
        )
        ProductCategory.objects.create(
            category=self.category_r1,
            product=self.product_r1,
        )
        ProductCategory.objects.create(
            category=self.category_r2,
            product=self.product_r2,
        )

    def authenticate(self):
        self.client.force_authenticate(user=self.user)

    @patch("catalogue.views.requests.get")
    def test_products_list_route_returns_stock_flags(self, mock_get):
        mock_get.return_value = Mock(
            status_code=200,
            json=Mock(
                return_value={
                    str(self.product_r1.id): True,
                    str(self.product_r2.id): False,
                }
            ),
        )

        response = self.client.get(reverse("product-list"))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
        payload = {item["id"]: item for item in response.data}
        self.assertTrue(payload[self.product_r1.id]["in_stock"])
        self.assertFalse(payload[self.product_r2.id]["in_stock"])

    @patch("catalogue.views.requests.get")
    def test_product_retrieve_route_returns_stock_flag(self, mock_get):
        mock_get.return_value = Mock(
            status_code=200,
            json=Mock(return_value={"available": True}),
        )

        response = self.client.get(
            reverse("product-detail", kwargs={"pk": self.product_r1.id})
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["id"], self.product_r1.id)
        self.assertTrue(response.data["in_stock"])

    def test_restaurant_products_route_filters_by_restaurant(self):
        response = self.client.get(
            reverse(
                "restaurant-products-list",
                kwargs={"restaurant_id": 1},
            )
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["id"], self.product_r1.id)

    def test_categories_routes_filter_by_restaurant(self):
        response_query = self.client.get(f'{reverse("category-list")}?restaurant_id=1')
        response_nested = self.client.get(
            reverse(
                "restaurant-categories-list",
                kwargs={"restaurant_id": 2},
            )
        )

        self.assertEqual(response_query.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response_query.data), 1)
        self.assertEqual(response_query.data[0]["id"], self.category_r1.id)

        self.assertEqual(response_nested.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response_nested.data), 1)
        self.assertEqual(response_nested.data[0]["id"], self.category_r2.id)

    def test_menus_routes_filter_by_restaurant(self):
        response_query = self.client.get(f'{reverse("menu-list")}?restaurant=1')
        response_nested = self.client.get(
            reverse(
                "restaurant-menus-list",
                kwargs={"restaurant_id": 2},
            )
        )

        self.assertEqual(response_query.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response_query.data), 1)
        self.assertEqual(response_query.data[0]["id"], self.menu_r1.id)

        self.assertEqual(response_nested.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response_nested.data), 1)
        self.assertEqual(response_nested.data[0]["id"], self.menu_r2.id)

    def test_menu_categories_nested_route_filters_by_menu(self):
        response = self.client.get(
            reverse(
                "menu-categories-list",
                kwargs={"menu_id": self.menu_r1.id},
            )
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["id"], self.menu_category_r1.id)

    def test_menu_products_nested_route_filters_by_menu(self):
        response = self.client.get(
            reverse(
                "menu-products-list",
                kwargs={"menu_id": self.menu_r1.id},
            )
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["product"], self.product_r1.id)

    def test_products_categories_route_filters_by_restaurant_query(self):
        response = self.client.get(f'{reverse("productcategory-list")}?restaurant_id=1')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["product"], self.product_r1.id)
        self.assertEqual(response.data[0]["category"], self.category_r1.id)

    def test_categories_menu_route_filters_by_restaurant_query(self):
        response = self.client.get(f'{reverse("categorymenu-list")}?restaurant=2')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["id"], self.menu_category_r2.id)

    def test_products_categories_menu_route_filters_by_restaurant_query(self):
        response = self.client.get(
            f'{reverse("productcategorymenu-list")}?restaurant_id=1'
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["product"], self.product_r1.id)
        self.assertEqual(response.data[0]["category"], self.menu_category_r1.id)

    def test_anonymous_cannot_create_product(self):
        payload = {
            "name": "Nouveau produit",
            "restaurant_id": 1,
            "description": "Test",
            "price": "8.50",
            "category": self.category_r1.id,
        }
        response = self.client.post(reverse("product-list"), data=payload, format="json")

        self.assertIn(
            response.status_code,
            (status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN),
        )

    def test_authenticated_can_create_product(self):
        self.authenticate()
        payload = {
            "name": "Wrap poulet",
            "restaurant_id": 1,
            "description": "Nouveau",
            "price": "9.90",
            "category": self.category_r1.id,
            "categories": [self.category_r1.id],
            "available": True,
        }

        response = self.client.post(reverse("product-list"), data=payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["name"], payload["name"])
        self.assertEqual(response.data["restaurant_id"], str(payload["restaurant_id"]))

    def test_authenticated_can_update_product(self):
        self.authenticate()
        payload = {
            "name": "Cheeseburger XL",
            "price": "11.50",
        }

        response = self.client.patch(
            reverse("product-detail", kwargs={"pk": self.product_r1.id}),
            data=payload,
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.product_r1.refresh_from_db()
        self.assertEqual(self.product_r1.name, payload["name"])
        self.assertEqual(str(self.product_r1.price), payload["price"])

    def test_authenticated_can_delete_product(self):
        self.authenticate()
        response = self.client.delete(
            reverse("product-detail", kwargs={"pk": self.product_r1.id})
        )

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Product.objects.filter(id=self.product_r1.id).exists())

    def test_authenticated_can_create_update_delete_category(self):
        self.authenticate()
        create_payload = {
            "restaurant_id": 1,
            "name": "Boissons",
            "description": "Softs",
        }
        create_response = self.client.post(
            reverse("category-list"), data=create_payload, format="json"
        )
        self.assertEqual(create_response.status_code, status.HTTP_201_CREATED)
        category_id = create_response.data["id"]

        update_response = self.client.patch(
            reverse("category-detail", kwargs={"pk": category_id}),
            data={"name": "Boissons fraiches"},
            format="json",
        )
        self.assertEqual(update_response.status_code, status.HTTP_200_OK)
        self.assertEqual(update_response.data["name"], "Boissons fraiches")

        delete_response = self.client.delete(
            reverse("category-detail", kwargs={"pk": category_id})
        )
        self.assertEqual(delete_response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Category.objects.filter(id=category_id).exists())

    def test_authenticated_can_create_update_delete_menu(self):
        self.authenticate()
        create_payload = {
            "restaurant_id": 1,
            "name": "Menu enfant",
            "description": "Petit menu",
            "price": "7.50",
        }
        create_response = self.client.post(
            reverse("menu-list"), data=create_payload, format="json"
        )
        self.assertEqual(create_response.status_code, status.HTTP_201_CREATED)
        menu_id = create_response.data["id"]

        update_response = self.client.patch(
            reverse("menu-detail", kwargs={"pk": menu_id}),
            data={"price": "8.00"},
            format="json",
        )
        self.assertEqual(update_response.status_code, status.HTTP_200_OK)
        self.assertEqual(update_response.data["price"], "8.00")

        delete_response = self.client.delete(
            reverse("menu-detail", kwargs={"pk": menu_id})
        )
        self.assertEqual(delete_response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Menu.objects.filter(id=menu_id).exists())

    def test_authenticated_can_create_update_delete_product_category_link(self):
        self.authenticate()
        product = Product.objects.create(
            restaurant_id=1,
            name="Nuggets",
            description="test",
            price="5.00",
            category=self.category_r1,
        )
        create_response = self.client.post(
            reverse("productcategory-list"),
            data={"category": self.category_r1.id, "product": product.id},
            format="json",
        )
        self.assertEqual(create_response.status_code, status.HTTP_201_CREATED)
        link_id = create_response.data["id"]

        update_response = self.client.patch(
            reverse("productcategory-detail", kwargs={"pk": link_id}),
            data={"category": self.category_r2.id},
            format="json",
        )
        self.assertEqual(update_response.status_code, status.HTTP_200_OK)
        self.assertEqual(update_response.data["category"], self.category_r2.id)


        delete_response = self.client.delete(
            reverse("productcategory-detail", kwargs={"pk": link_id})
        )
        self.assertEqual(delete_response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(ProductCategory.objects.filter(id=link_id).exists())


class CatalogueDatabaseIntegrationTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.publish_event_patcher = patch("catalogue.signals.publish_catalogue_event")
        cls.publish_event_patcher.start()

    @classmethod
    def tearDownClass(cls):
        cls.publish_event_patcher.stop()
        super().tearDownClass()

    def test_database_connection_executes_basic_query(self):
        db = connections["default"]
        db.ensure_connection()
        with db.cursor() as cursor:
            cursor.execute("SELECT 1")
            row = cursor.fetchone()
        self.assertEqual(row[0], 1)

    def test_database_persists_and_reads_catalogue_entities(self):
        category = Category.objects.create(
            restaurant_id="test_id",
            name="Integration Category",
            description="db test",
        )
        product = Product.objects.create(
            restaurant_id="test_id",
            name="Integration Product",
            description="db test",
            price="14.20",
            category=category,
        )

        fetched = Product.objects.select_related("category").get(id=product.id)
        self.assertEqual(fetched.name, "Integration Product")
        self.assertEqual(fetched.category.id, category.id)
        self.assertEqual(fetched.restaurant_id, "test_id")

    def test_database_cascade_delete_menu_removes_menu_categories(self):
        menu = Menu.objects.create(
            restaurant_id="test_id",
            name="Integration Menu",
            description="db cascade",
            price="12.00",
        )
        category_menu = CategoryMenu.objects.create(
            menu=menu,
            name="Cascade Category",
            quantity=1,
        )

        menu.delete()
        self.assertFalse(CategoryMenu.objects.filter(id=category_menu.id).exists())
