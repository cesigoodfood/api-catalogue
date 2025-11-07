from rest_framework import viewsets, permissions, filters
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
        try:
            rid_int = int(rid)
        except (TypeError, ValueError):
            return qs.none()
        return qs.filter(restaurant_id=rid_int)


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
        try:
            rid_int = int(rid)
        except (TypeError, ValueError):
            return qs.none()
        return qs.filter(restaurant_id=rid_int)


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
        try:
            rid_int = int(rid)
        except (TypeError, ValueError):
            return qs.none()
        return qs.filter(restaurant_id=rid_int)

class ProductCategoryViewSet(viewsets.ModelViewSet):
    queryset = ProductCategory.objects.all()
    serializer_class = ProductCategorySerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        qs = super().get_queryset().select_related('product')
        rid = self.kwargs.get('restaurant_id') or self.request.query_params.get('restaurant_id') or self.request.query_params.get('restaurant')
        if rid is None:
            return qs
        try:
            rid_int = int(rid)
        except (TypeError, ValueError):
            return qs.none()
        return qs.filter(product__restaurant_id=rid_int)


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
        try:
            rid_int = int(rid)
        except (TypeError, ValueError):
            return qs.none()
        return qs.filter(menu__restaurant_id=rid_int)


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
        try:
            rid_int = int(rid)
        except (TypeError, ValueError):
            return qs.none()
        return qs.filter(product__restaurant_id=rid_int)
