from django.db import models


class TimestampedModel(models.Model):
    """Abstract model to add createdAt / updatedAt / deletedAt columns with exact DB column names."""
    created_at = models.DateTimeField(auto_now_add=True, db_column='createdAt')
    updated_at = models.DateTimeField(auto_now=True, db_column='updatedAt')
    deleted_at = models.DateTimeField(null=True, blank=True, db_column='deletedAt')

    class Meta:
        abstract = True


class Menu(TimestampedModel):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    image_url = models.URLField(max_length=500, blank=True, null=True, db_column='imageUrl')
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    restaurant_id = models.BigIntegerField(db_index=True, db_column='restaurantId')

    class Meta:
        db_table = 'menus'

    def __str__(self):
        return self.name


class Category(TimestampedModel):
    restaurant_id = models.BigIntegerField(db_index=True, db_column='restaurantId')
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    image_url = models.URLField(max_length=500, blank=True, null=True, db_column='imageUrl')

    class Meta:
        db_table = 'categories'

    def __str__(self):
        return self.name


class CategoryMenu(models.Model):
    """Categories attached to a Menu (categories_menu table)."""
    menu = models.ForeignKey('Menu', on_delete=models.CASCADE, db_column='menuId', related_name='categories_menu')
    name = models.CharField(max_length=255)
    quantity = models.IntegerField(default=0)

    class Meta:
        db_table = 'categories_menu'

    def __str__(self):
        return f"{self.menu} - {self.name}"


class Product(TimestampedModel):
    name = models.CharField(max_length=255)
    restaurant_id = models.BigIntegerField(db_index=True, db_column='restaurantId')
    description = models.TextField(blank=True, null=True)
    image_url = models.URLField(max_length=500, blank=True, null=True, db_column='imageUrl')
    price = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.ForeignKey('Category', on_delete=models.SET_NULL, null=True, blank=True, db_column='categoryId', related_name='primary_products')
    available = models.BooleanField(default=True)
    categories = models.ManyToManyField('Category', through='ProductCategory', related_name='products', blank=True)

    class Meta:
        db_table = 'products'

    def __str__(self):
        return self.name


class ProductCategory(models.Model):
    """Join table products_category linking products <-> categories."""
    category = models.ForeignKey('Category', on_delete=models.CASCADE, db_column='categoryId')
    product = models.ForeignKey('Product', on_delete=models.CASCADE, db_column='productId')

    class Meta:
        db_table = 'products_category'
        unique_together = (('category', 'product'),)

    def __str__(self):
        return f"{self.product} in {self.category}"


class ProductCategoryMenu(models.Model):
    """Join table products_category_menu linking products <-> categories_menu (products within a menu category)."""
    category = models.ForeignKey('CategoryMenu', on_delete=models.CASCADE, db_column='categoryId', related_name='product_links')
    product = models.ForeignKey('Product', on_delete=models.CASCADE, db_column='productId')

    class Meta:
        db_table = 'products_category_menu'
        unique_together = (('category', 'product'),)

    def __str__(self):
        return f"{self.product} in {self.category} (menu)"
