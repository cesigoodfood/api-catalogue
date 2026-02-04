from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.forms.models import model_to_dict

from .models import Product, Category, Menu, ProductCategory, CategoryMenu, ProductCategoryMenu
from .events import publish_catalogue_event


def _publish(instance, action: str):
    payload = model_to_dict(instance)
    publish_catalogue_event(instance.__class__.__name__.lower(), action, getattr(instance, 'id', None), payload)


@receiver(post_save, sender=Product)
@receiver(post_save, sender=Category)
@receiver(post_save, sender=Menu)
@receiver(post_save, sender=ProductCategory)
@receiver(post_save, sender=CategoryMenu)
@receiver(post_save, sender=ProductCategoryMenu)
def on_save(sender, instance, created, **kwargs):
    action = 'created' if created else 'updated'
    _publish(instance, action)


@receiver(post_delete, sender=Product)
@receiver(post_delete, sender=Category)
@receiver(post_delete, sender=Menu)
@receiver(post_delete, sender=ProductCategory)
@receiver(post_delete, sender=CategoryMenu)
@receiver(post_delete, sender=ProductCategoryMenu)
def on_delete(sender, instance, **kwargs):
    _publish(instance, 'deleted')
