from django.contrib import admin
from core.models import *


@admin.register(Owner)
class OwnerAdmin(admin.ModelAdmin):
    list_display = ['name', 'created_by', 'created_at', 'updated_at']
    list_filter = ['created_at', 'updated_at', 'created_by']
    search_fields = ['name']
    fields = ['name', 'created_by', 'created_at', 'updated_at']
    
    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        if not obj:  # New object
            from django.utils import timezone
            form.base_fields['created_at'].initial = timezone.now()
            form.base_fields['updated_at'].initial = timezone.now()
        return form


@admin.register(Account)
class AccountAdmin(admin.ModelAdmin):
    list_display = ['name', 'account_number', 'account_type', 'created_by', 'created_at', 'updated_at']
    list_filter = ['account_type', 'created_at', 'updated_at', 'created_by']
    search_fields = ['name', 'account_number']
    fields = ['name', 'account_number', 'account_type', 'created_by', 'created_at', 'updated_at']
    
    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        if not obj:  # New object
            from django.utils import timezone
            form.base_fields['created_at'].initial = timezone.now()
            form.base_fields['updated_at'].initial = timezone.now()
        return form


@admin.register(Jar)
class JarAdmin(admin.ModelAdmin):
    list_display = ['name', 'account', 'owner', 'balance', 'created_at', 'updated_at']
    list_filter = ['account', 'owner', 'created_at', 'updated_at']
    search_fields = ['name', 'account__name', 'owner__name']
    fields = ['name', 'account', 'balance', 'owner', 'created_at', 'updated_at']
    
    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        if not obj:  # New object
            from django.utils import timezone
            form.base_fields['created_at'].initial = timezone.now()
            form.base_fields['updated_at'].initial = timezone.now()
        return form


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ['__str__', 'transaction_type', 'amount', 'jar', 'created_at', 'updated_at']
    list_filter = ['transaction_type', 'created_at', 'updated_at', 'created_by']
    search_fields = ['source_destination', 'description', 'jar__name']
    fields = ['jar', 'transaction_type', 'amount', 'source_destination', 'description', 
              'destination_jar', 'created_by', 'created_at', 'updated_at']
    
    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        if not obj:  # New object
            from django.utils import timezone
            now = timezone.now()
            form.base_fields['created_at'].initial = now
            form.base_fields['updated_at'].initial = now
        return form
