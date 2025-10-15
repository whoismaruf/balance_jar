from django.db import models
from django.contrib.auth.models import User
from django.db.models import Sum


# Create your models here.

class BaseModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Owner(BaseModel):
    name = models.CharField(max_length=100)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.name
    
    def total_balance(self):
        return self.jar_set.aggregate(total=Sum('balance'))['total'] or 0


class Account(BaseModel):
    ACCOUNT_TYPE_CHOICES = [
        ('SAVINGS', 'Savings'),
        ('CHECKING', 'Checking'),
        ('CREDIT', 'Credit'),
        ('CASH', 'Cash'),
    ]
    name = models.CharField(max_length=100)
    account_number = models.CharField(max_length=20)
    account_type = models.CharField(max_length=10, choices=ACCOUNT_TYPE_CHOICES, default="CASH")
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.name} <{self.created_by.username}>"

    def total_balance(self):
        return self.jar_set.aggregate(total=Sum('balance'))['total'] or 0


class Jar(BaseModel):
    name = models.CharField(max_length=100)
    account = models.ForeignKey(Account, on_delete=models.CASCADE)
    balance = models.DecimalField(max_digits=10, decimal_places=2)
    owner = models.ForeignKey(Owner, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.name} - {self.owner.name}"

    def add_money(self, amount):
        """Add money to the jar balance"""
        self.balance += amount
        self.save()

    def remove_money(self, amount):
        """Remove money from the jar balance"""
        if self.balance >= amount:
            self.balance -= amount
            self.save()
            return True
        return False


class Transaction(BaseModel):
    TRANSACTION_TYPE_CHOICES = [
        ('INCOMING', 'Incoming'),
        ('OUTGOING', 'Outgoing'),
        ('TRANSFER', 'Transfer'),
    ]
    
    jar = models.ForeignKey(Jar, on_delete=models.CASCADE, related_name='transactions')
    transaction_type = models.CharField(max_length=10, choices=TRANSACTION_TYPE_CHOICES)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    source_destination = models.CharField(max_length=200, help_text="Where the money comes from or goes to")
    description = models.TextField(blank=True, null=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    
    # Transfer-specific fields
    destination_jar = models.ForeignKey(
        Jar, 
        on_delete=models.CASCADE, 
        related_name='incoming_transfers',
        null=True, 
        blank=True,
        help_text="Destination jar for transfers"
    )

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        if self.transaction_type == 'TRANSFER':
            return f"Transfer - {self.amount} ({self.jar.name} → {self.destination_jar.name})"
        return f"{self.get_transaction_type_display()} - {self.amount} ({self.jar.name})"

    def save(self, *args, **kwargs):
        """Override save to update jar balance automatically"""
        is_new = self.pk is None
        
        if is_new:
            # Update jar balance based on transaction type
            if self.transaction_type == 'INCOMING':
                self.jar.add_money(self.amount)
            elif self.transaction_type == 'OUTGOING':
                if not self.jar.remove_money(self.amount):
                    raise ValueError("Insufficient balance in jar")
            elif self.transaction_type == 'TRANSFER':
                if not self.destination_jar:
                    raise ValueError("Destination jar is required for transfers")
                if self.jar == self.destination_jar:
                    raise ValueError("Cannot transfer to the same jar")
                
                # Remove money from source jar
                if not self.jar.remove_money(self.amount):
                    raise ValueError("Insufficient balance in source jar")
                
                # Add money to destination jar
                self.destination_jar.add_money(self.amount)
                
                # Update source_destination for display
                self.source_destination = f"{self.destination_jar.name} ({self.destination_jar.account.name})"
        
        super().save(*args, **kwargs)