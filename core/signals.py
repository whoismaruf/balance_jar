# signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import *


@receiver(post_save, sender=User)
def create_owner_for_user(sender, instance, created, **kwargs):
    if created:
        Owner.objects.create(created_by=instance, name="Self")


@receiver(post_save, sender=Account)
def create_main_jar_for_account(sender, instance, created, **kwargs):
    if created:
        try:
            owner = Owner.objects.get(created_by=instance.created_by, name="Self")
            Jar.objects.create(
                name="Main",
                account=instance,
                balance=0,
                owner=owner
            )
        except Owner.DoesNotExist:
            # Optional: log or handle missing owner
            print("Owner with name 'Self' does not exist for user:", instance.created_by)
            pass
