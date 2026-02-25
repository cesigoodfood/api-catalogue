from django.urls import include, path
from rest_framework.routers import DefaultRouter
from .views import (
    ProductViewSet,
    CategoryViewSet,
    MenuViewSet,
    ProductCategoryViewSet,
    CategoryMenuViewSet,
    ProductCategoryMenuViewSet,
)

router = DefaultRouter()
router.register(r'products', ProductViewSet, basename='product')
router.register(r'categories', CategoryViewSet, basename='category')
router.register(r'menus', MenuViewSet, basename='menu')
router.register(r'products-categories', ProductCategoryViewSet, basename='productcategory')
router.register(r'categories-menu', CategoryMenuViewSet, basename='categorymenu')
router.register(r'products-categories-menu', ProductCategoryMenuViewSet, basename='productcategorymenu')

urlpatterns = [
    path('', include(router.urls)),
    # nested endpoints for restaurants
    path('restaurants/<str:restaurant_id>/products/', ProductViewSet.as_view({'get': 'list', 'post': 'create'}), name='restaurant-products-list'),
    path('restaurants/<str:restaurant_id>/products/<int:pk>/', ProductViewSet.as_view({'get': 'retrieve', 'put': 'update', 'patch': 'partial_update', 'delete': 'destroy'}), name='restaurant-products-detail'),
    path('restaurants/<str:restaurant_id>/categories/', CategoryViewSet.as_view({'get': 'list', 'post': 'create'}), name='restaurant-categories-list'),
    path('restaurants/<str:restaurant_id>/categories/<int:pk>/', CategoryViewSet.as_view({'get': 'retrieve', 'put': 'update', 'patch': 'partial_update', 'delete': 'destroy'}), name='restaurant-categories-detail'),
    path('restaurants/<str:restaurant_id>/menus/', MenuViewSet.as_view({'get': 'list', 'post': 'create'}), name='restaurant-menus-list'),
    path('restaurants/<str:restaurant_id>/menus/<int:pk>/', MenuViewSet.as_view({'get': 'retrieve', 'put': 'update', 'patch': 'partial_update', 'delete': 'destroy'}), name='restaurant-menus-detail'),

    # nested endpoints for menus
    path('menus/<int:menu_id>/categories/', CategoryMenuViewSet.as_view({'get': 'list', 'post': 'create'}), name='menu-categories-list'),
    path('menus/<int:menu_id>/categories/<int:pk>/', CategoryMenuViewSet.as_view({'get': 'retrieve', 'put': 'update', 'patch': 'partial_update', 'delete': 'destroy'}), name='menu-categories-detail'),
    path('menus/<int:menu_id>/products/', ProductCategoryMenuViewSet.as_view({'get': 'list', 'post': 'create'}), name='menu-products-list'),
    path('menus/<int:menu_id>/products/<int:pk>/', ProductCategoryMenuViewSet.as_view({'get': 'retrieve', 'put': 'update', 'patch': 'partial_update', 'delete': 'destroy'}), name='menu-products-detail'),
]
