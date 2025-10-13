from core.models import *
from django import forms


class OwnerForm(forms.ModelForm):
    class Meta:
        model = Owner
        fields = ['name']


class AccountForm(forms.ModelForm):
    class Meta:
        model = Account
        fields = ['name', 'account_number', 'account_type']
        account_type = forms.ChoiceField(choices=Account.ACCOUNT_TYPE_CHOICES, initial='CASH')


class JarForm(forms.ModelForm):
    class Meta:
        model = Jar
        fields = ['name', 'account', 'balance', 'owner']
        account = forms.ModelChoiceField(queryset=Account.objects.all())
        owner = forms.ModelChoiceField(queryset=Owner.objects.all())
        balance = forms.DecimalField(max_digits=10, decimal_places=2, initial=0.00)


class JarFormNoAccount(forms.ModelForm):
    class Meta:
        model = Jar
        fields = ['name', 'balance', 'owner']
        owner = forms.ModelChoiceField(queryset=Owner.objects.all())
        balance = forms.DecimalField(max_digits=10, decimal_places=2, initial=0.00)


class TransactionForm(forms.ModelForm):
    class Meta:
        model = Transaction
        fields = ['transaction_type', 'amount', 'source_destination', 'description']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
            'amount': forms.NumberInput(attrs={'step': '0.01', 'min': '0.01'}),
            'source_destination': forms.TextInput(attrs={'placeholder': 'e.g., Salary, Grocery Store, ATM, etc.'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['transaction_type'].widget.attrs.update({'class': 'form-select'})
        self.fields['amount'].widget.attrs.update({'class': 'form-control'})
        self.fields['source_destination'].widget.attrs.update({'class': 'form-control'})
        self.fields['description'].widget.attrs.update({'class': 'form-control'})


class IncomingTransactionForm(forms.ModelForm):
    class Meta:
        model = Transaction
        fields = ['amount', 'source_destination', 'description']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
            'amount': forms.NumberInput(attrs={'step': '0.01', 'min': '0.01'}),
            'source_destination': forms.TextInput(attrs={'placeholder': 'e.g., Salary, Bonus, Gift, etc.'}),
        }

    def save(self, commit=True):
        transaction = super().save(commit=False)
        transaction.transaction_type = 'INCOMING'
        if commit:
            transaction.save()
        return transaction


class OutgoingTransactionForm(forms.ModelForm):
    class Meta:
        model = Transaction
        fields = ['amount', 'source_destination', 'description']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
            'amount': forms.NumberInput(attrs={'step': '0.01', 'min': '0.01'}),
            'source_destination': forms.TextInput(attrs={'placeholder': 'e.g., Grocery Store, Rent, Bill Payment, etc.'}),
        }

    def __init__(self, *args, **kwargs):
        self.jar = kwargs.pop('jar', None)
        super().__init__(*args, **kwargs)

    def clean_amount(self):
        amount = self.cleaned_data.get('amount')
        if self.jar and amount and amount > self.jar.balance:
            raise forms.ValidationError(f"Insufficient balance. Available: {self.jar.balance}")
        return amount

    def save(self, commit=True):
        transaction = super().save(commit=False)
        transaction.transaction_type = 'OUTGOING'
        if commit:
            transaction.save()
        return transaction
