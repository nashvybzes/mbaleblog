from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.utils import timezone
from .models import Poll

@receiver(pre_save, sender=Poll)
def update_poll_status(sender, instance, **kwargs):
    now = timezone.now()
    if instance.start_time <= now <= instance.end_time:
        instance.is_active = True
    else:
        instance.is_active = False