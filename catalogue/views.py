from rest_framework import viewsets, permissions, filters, status
from rest_framework.response import Response
from django.conf import settings
import requests
from .models import Product, Category, Menu, ProductCategory, CategoryMenu, ProductCategoryMenu
from .serializers import (
    ProductSerializer,
    CategorySerializer,
    MenuSerializer,
    ProductCategorySerializer,
    CategoryMenuSerializer,
    ProductCategoryMenuSerializer,
)


class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [filters.SearchFilter]
    search_fields = ['name', 'description']

    def get_queryset(self):
        qs = super().get_queryset()
        rid = self.kwargs.get('restaurant_id') or self.request.query_params.get('restaurant_id') or self.request.query_params.get('restaurant')
        if rid is None:
            return qs
        return qs.filter(restaurant_id=rid)

    def retrieve(self, request, *args, **kwargs):
        response = super().retrieve(request, *args, **kwargs)
        if response.status_code != status.HTTP_200_OK:
            return response
        product_id = response.data.get('id')
        in_stock = None
        base = getattr(settings, 'STOCK_API_BASE', '').rstrip('/')
        if base and product_id is not None:
            try:
                url = f"{base}/products/{product_id}/availability/"
                stock_resp = requests.get(url, timeout=2)
                if stock_resp.status_code == 200:
                    payload = stock_resp.json()
                    in_stock = bool(payload.get('available'))
            except Exception:
                in_stock = None
        response.data['in_stock'] = in_stock
        return response

    def list(self, request, *args, **kwargs):
        response = super().list(request, *args, **kwargs)
        if response.status_code != status.HTTP_200_OK:
            return response
        data = response.data
        items = data.get('results') if isinstance(data, dict) else data
        if not isinstance(items, list):
            return response
        ids = [item.get('id') for item in items if isinstance(item, dict) and item.get('id') is not None]
        in_stock_map = {}
        base = getattr(settings, 'STOCK_API_BASE', '').rstrip('/')
        if base and ids:
            try:
                url = f"{base}/products/availability/"
                params = {'ids': ','.join(str(i) for i in ids)}
                stock_resp = requests.get(url, params=params, timeout=2)
                if stock_resp.status_code == 200:
                    payload = stock_resp.json()
                    if isinstance(payload, dict):
                        in_stock_map = payload
            except Exception:
                in_stock_map = {}
        for item in items:
            pid = item.get('id')
            if pid is None:
                item['in_stock'] = None
                continue
            item['in_stock'] = bool(in_stock_map.get(str(pid))) if in_stock_map else None
        return response


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [filters.SearchFilter]
    search_fields = ['name']

    def get_queryset(self):
        qs = super().get_queryset()
        rid = self.kwargs.get('restaurant_id') or self.request.query_params.get('restaurant_id') or self.request.query_params.get('restaurant')
        if rid is None:
            return qs
        return qs.filter(restaurant_id=rid)


class MenuViewSet(viewsets.ModelViewSet):
    queryset = Menu.objects.all()
    serializer_class = MenuSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [filters.SearchFilter]
    search_fields = ['name']

    def get_queryset(self):
        qs = super().get_queryset()
        # support both query param and nested URL kwarg 'restaurant_id'
        rid = self.kwargs.get('restaurant_id') or self.request.query_params.get('restaurant_id') or self.request.query_params.get('restaurant')
        if rid is None:
            return qs
        return qs.filter(restaurant_id=rid)

class ProductCategoryViewSet(viewsets.ModelViewSet):
    queryset = ProductCategory.objects.all()
    serializer_class = ProductCategorySerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        qs = super().get_queryset().select_related('product')
        rid = self.kwargs.get('restaurant_id') or self.request.query_params.get('restaurant_id') or self.request.query_params.get('restaurant')
        if rid is None:
            return qs
        return qs.filter(product__restaurant_id=rid)


class CategoryMenuViewSet(viewsets.ModelViewSet):
    queryset = CategoryMenu.objects.select_related('menu').all()
    serializer_class = CategoryMenuSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        qs = super().get_queryset()
        # allow nested /menus/{menu_id}/categories/ or /restaurants/{restaurant_id}/categories-menu/
        menu_id = self.kwargs.get('menu_id')
        if menu_id is not None:
            try:
                mid = int(menu_id)
            except (TypeError, ValueError):
                return qs.none()
            return qs.filter(menu_id=mid)
        rid = self.kwargs.get('restaurant_id') or self.request.query_params.get('restaurant_id') or self.request.query_params.get('restaurant')
        if rid is None:
            return qs
        return qs.filter(menu__restaurant_id=rid)


class ProductCategoryMenuViewSet(viewsets.ModelViewSet):
    queryset = ProductCategoryMenu.objects.all()
    serializer_class = ProductCategoryMenuSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        qs = super().get_queryset().select_related('product')
        # support nested /menus/{menu_id}/products/ (filter by category__menu_id)
        menu_id = self.kwargs.get('menu_id')
        if menu_id is not None:
            try:
                mid = int(menu_id)
            except (TypeError, ValueError):
                return qs.none()
            return qs.filter(category__menu_id=mid)
        rid = self.kwargs.get('restaurant_id') or self.request.query_params.get('restaurant_id') or self.request.query_params.get('restaurant')
        if rid is None:
            return qs
        return qs.filter(product__restaurant_id=rid)
