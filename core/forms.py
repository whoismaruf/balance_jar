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


class TransferForm(forms.ModelForm):
    source_jar = forms.ModelChoiceField(
        queryset=Jar.objects.all(),
        widget=forms.Select(attrs={'class': 'form-select'}),
        help_text="Select the jar to transfer money FROM",
        empty_label="-- Select source jar --"
    )
    destination_jar = forms.ModelChoiceField(
        queryset=Jar.objects.all(),
        widget=forms.Select(attrs={'class': 'form-select'}),
        help_text="Select the jar to transfer money TO",
        empty_label="-- Select destination jar --"
    )

    class Meta:
        model = Transaction
        fields = ['source_jar', 'destination_jar', 'amount', 'description']
        widgets = {
            'description': forms.Textarea(attrs={
                'rows': 3,
                'class': 'form-control',
                'placeholder': 'Optional: Add notes about this transfer...'
            }),
            'amount': forms.NumberInput(attrs={
                'step': '0.01',
                'min': '0.01',
                'class': 'form-control',
                'placeholder': '0.00'
            }),
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        # Filter jars by user and customize display
        if self.user:
            user_jars = Jar.objects.filter(account__created_by=self.user).select_related('account', 'owner')
            self.fields['source_jar'].queryset = user_jars
            self.fields['destination_jar'].queryset = user_jars
            
            # Customize the choice labels to show account and balance info
            jar_choices = []
            for jar in user_jars:
                label = f"{jar.name} - {jar.account.name} (Balance: {jar.balance}) - {jar.owner.name}"
                jar_choices.append((jar.id, label))
            
            self.fields['source_jar'].choices = [('', '---------')] + jar_choices
            self.fields['destination_jar'].choices = [('', '---------')] + jar_choices

    def clean(self):
        cleaned_data = super().clean()
        source_jar = cleaned_data.get('source_jar')
        destination_jar = cleaned_data.get('destination_jar')
        amount = cleaned_data.get('amount')

        if source_jar and destination_jar:
            # Check if trying to transfer to the same jar
            if source_jar == destination_jar:
                raise forms.ValidationError("Cannot transfer money to the same jar.")
            
            # Check if source jar has sufficient balance
            if amount and amount > source_jar.balance:
                raise forms.ValidationError(
                    f"Insufficient balance in {source_jar.name}. "
                    f"Available: {source_jar.balance}, Requested: {amount}"
                )

        return cleaned_data

    def save(self, commit=True):
        transaction = super().save(commit=False)
        transaction.transaction_type = 'TRANSFER'
        transaction.jar = self.cleaned_data['source_jar']
        transaction.destination_jar = self.cleaned_data['destination_jar']
        
        if commit:
            transaction.save()
        return transaction
