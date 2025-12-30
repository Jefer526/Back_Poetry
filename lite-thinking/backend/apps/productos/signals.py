"""
Signals para la app Productos - VERSIÓN FINAL
Crea automáticamente el inventario cuando se crea un producto
"""
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Producto


@receiver(post_save, sender=Producto)
def crear_inventario_automatico(sender, instance, created, **kwargs):
    """
    Cuando se crea un producto, crear automáticamente su inventario
    con cantidad inicial en 0
    """
    if created:
        from backend.apps.inventario.models import Inventario
        
        if not hasattr(instance, 'inventario'):
            Inventario.objects.create(
                producto=instance,
                cantidad_actual=0,
                ubicacion=""
            )
            print(f"✓ Inventario creado automáticamente para: {instance.codigo}")