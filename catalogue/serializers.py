from rest_framework import serializers
from .models import Product, Category, Menu, ProductCategory, CategoryMenu, ProductCategoryMenu


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ('id', 'restaurant_id', 'name', 'description', 'image_url', 'created_at', 'updated_at', 'deleted_at')


class MenuSerializer(serializers.ModelSerializer):
    class Meta:
        model = Menu
        fields = ('id', 'name', 'description', 'image_url', 'price', 'restaurant_id', 'created_at', 'updated_at', 'deleted_at')


class ProductSerializer(serializers.ModelSerializer):
    # categories displayed as list of PKs and writable
    categories = serializers.PrimaryKeyRelatedField(many=True, queryset=Category.objects.all(), required=False)
    category = serializers.PrimaryKeyRelatedField(queryset=Category.objects.all(), allow_null=True, required=False)

    class Meta:
        model = Product
        fields = (
            'id', 'name', 'restaurant_id', 'description', 'image_url', 'price', 'category', 'categories', 'available', 'created_at', 'updated_at', 'deleted_at'
        )

    def create(self, validated_data):
        categories = validated_data.pop('categories', [])
        product = Product.objects.create(**validated_data)
        if categories:
            product.categories.set(categories)
        return product

    def update(self, instance, validated_data):
        categories = validated_data.pop('categories', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        if categories is not None:
            instance.categories.set(categories)
        return instance


class ProductCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductCategory
        fields = ('id', 'category', 'product')


class CategoryMenuSerializer(serializers.ModelSerializer):
    class Meta:
        model = CategoryMenu
        fields = ('id', 'menu', 'name', 'quantity')


class ProductCategoryMenuSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductCategoryMenu
        fields = ('id', 'category', 'product')