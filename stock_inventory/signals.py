from django.db.models.signals import post_save, post_delete, pre_save
from django.contrib.auth.signals import user_logged_in
from django.dispatch import receiver
from django.forms.models import model_to_dict
from .models import Product, StockMovement, AuditLog
from .middleware import get_current_user, get_current_ip

def create_audit_entry(action, model_name, description, instance=None):
    user = get_current_user()
    ip = get_current_ip()
    
    # Si no hay usuario (ej. script de consola o fixture), intentamos tomarlo del instance si existe
    if not user and instance and hasattr(instance, 'user') and instance.user:
         pass # Podríamos asignar lógica aquí, pero asumiremos null

    AuditLog.objects.create(
        user=user,
        action=action,
        model_name=model_name,
        description=description,
        ip_address=ip
    )

# --- SIGNALS PARA PRODUCTOS ---

@receiver(pre_save, sender=Product)
def product_pre_save(sender, instance, **kwargs):
    # Guardamos el estado anterior para comparar en UPDATE
    if instance.pk:
        try:
            old_instance = Product.objects.get(pk=instance.pk)
            instance._old_state = model_to_dict(old_instance)
        except Product.DoesNotExist:
            instance._old_state = {}
    else:
        instance._old_state = {}

@receiver(post_save, sender=Product)
def product_post_save(sender, instance, created, **kwargs):
    model_name = "PRODUCT"
    
    if created:
        desc = f"Producto creado: {instance.sku} - {instance.name}"
        create_audit_entry("CREATE", model_name, desc)
    else:
        # Detectar cambios
        changes = []
        if hasattr(instance, '_old_state'):
            new_state = model_to_dict(instance)
            for key, val in new_state.items():
                if key in instance._old_state and instance._old_state[key] != val:
                    changes.append(f"{key}: '{instance._old_state[key]}' -> '{val}'")
            
        desc = f"Producto actualizado ({instance.sku}). Cambios: {', '.join(changes)}"
        # Solo registramos si hubo cambios reales
        if changes: 
            create_audit_entry("UPDATE", model_name, desc)

@receiver(post_delete, sender=Product)
def product_post_delete(sender, instance, **kwargs):
    desc = f"Producto eliminado: {instance.sku} - {instance.name}"
    create_audit_entry("DELETE", "PRODUCT", desc)

# --- SIGNALS PARA MOVIMIENTOS ---

@receiver(post_save, sender=StockMovement)
def movement_post_save(sender, instance, created, **kwargs):
    if created:
        desc = f"Movimiento registrado: {instance.movement_type} de {instance.quantity} u. para {instance.product.sku}"
        create_audit_entry("CREATE", "MOVEMENT", desc)

# --- SIGNAL PARA LOGIN ---

@receiver(user_logged_in)
def log_user_login(sender, request, user, **kwargs):
    # user_logged_in envía el request directamente, no necesitamos el middleware aquí stricto sensu, 
    # pero usaremos la misma lógica para consistencia IP
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    ip = x_forwarded_for.split(',')[0] if x_forwarded_for else request.META.get('REMOTE_ADDR')
    
    AuditLog.objects.create(
        user=user,
        action="LOGIN",
        model_name="AUTH",
        description=f"Usuario {user.username} inició sesión",
        ip_address=ip
    )