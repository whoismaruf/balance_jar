from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from core.models import *
from core.forms import *


@login_required
def home(request):
    # Get all accounts for the current user
    accounts = Account.objects.filter(created_by=request.user)
    
    # Calculate total balance and jar count efficiently
    total_balance = 0
    total_jars = 0
    
    for account in accounts:
        total_balance += account.total_balance()
        total_jars += account.jar_set.count()
    
    # Get recent transactions
    user_jars = Jar.objects.filter(account__in=accounts)
    recent_transactions = Transaction.objects.filter(jar__in=user_jars).select_related('jar', 'jar__account', 'jar__owner').order_by('-created_at')[:5]
    
    # Calculate transaction statistics
    all_transactions = Transaction.objects.filter(jar__in=user_jars)
    total_income = sum(t.amount for t in all_transactions if t.transaction_type == 'INCOMING')
    total_expenses = sum(t.amount for t in all_transactions if t.transaction_type == 'OUTGOING')
    total_transactions = all_transactions.count()
    
    context = {
        'total_balance': total_balance,
        'total_jars': total_jars,
        'account_count': accounts.count(),
        'recent_transactions': recent_transactions,
        'total_income': total_income,
        'total_expenses': total_expenses,
        'total_transactions': total_transactions,
    }
    
    return render(request, 'core/index.html', context)


@login_required
def owner_view(request):
    owners = Owner.objects.all()
    form = OwnerForm()
    owner_forms_dict = {owner.id: OwnerForm(instance=owner) for owner in owners}

    # Calculate statistics
    total_jars = sum(owner.jar_set.count() for owner in owners)
    active_owners = sum(1 for owner in owners if owner.jar_set.count() > 0)

    if request.method == 'POST':
        if 'delete_id' in request.POST:
            owner = get_object_or_404(Owner, id=request.POST['delete_id'])
            owner.delete()
            return redirect('owner_view')
        elif 'update_id' in request.POST:
            owner = get_object_or_404(Owner, id=request.POST['update_id'])
            update_form = OwnerForm(request.POST, instance=owner)
            if update_form.is_valid():
                update_form.save()
                return redirect('owner_view')
        else:
            form = OwnerForm(request.POST)
            if form.is_valid():
                owner = form.save(commit=False)
                owner.created_by = request.user
                owner.save()
                return redirect('owner_view')

    return render(request, 'core/owner.html', {
        'owners': owners,
        'form': form,
        'owner_forms_dict': owner_forms_dict,
        'total_jars': total_jars,
        'active_owners': active_owners,
    })


@login_required
def account_view(request):
    accounts = Account.objects.filter(created_by=request.user)
    form = AccountForm()
    account_forms_dict = {account.id: AccountForm(instance=account) for account in accounts}
    
    # Calculate transaction counts for each account
    account_transaction_counts = {}
    for account in accounts:
        transaction_count = Transaction.objects.filter(jar__account=account).count()
        account_transaction_counts[account.id] = transaction_count

    if request.method == 'POST':
        if 'delete_id' in request.POST:
            account = get_object_or_404(Account, id=request.POST['delete_id'])
            account.delete()
            return redirect('account_view')
        elif 'update_id' in request.POST:
            account = get_object_or_404(Account, id=request.POST['update_id'])
            update_form = AccountForm(request.POST, instance=account)
            if update_form.is_valid():
                update_form.save()
                return redirect('account_view')
        else:
            form = AccountForm(request.POST)
            if form.is_valid():
                account = form.save(commit=False)
                account.created_by = request.user
                account.save()
                return redirect('account_view')

    return render(request, 'core/account.html', {
        'accounts': accounts,
        'form': form,
        'account_forms_dict': account_forms_dict,
        'account_transaction_counts': account_transaction_counts
    })


@login_required
def account_detail_view(request, account_id):
    account = get_object_or_404(Account, id=account_id, created_by=request.user)
    jars = account.jar_set.all()
    form = JarFormNoAccount()
    jar_forms_dict = {jar.id: JarFormNoAccount(instance=jar) for jar in jars}

    if request.method == 'POST':
        if 'delete_id' in request.POST:
            jar = get_object_or_404(Jar, id=request.POST['delete_id'])
            jar.delete()
            return redirect(reverse('account_detail', args=[account_id]))
        elif 'update_id' in request.POST:
            jar = get_object_or_404(Jar, id=request.POST['update_id'])
            update_form = JarFormNoAccount(request.POST, instance=jar)
            if update_form.is_valid():
                update_form.save()
                return redirect(reverse('account_detail', args=[account_id]))
        else:
            form = JarFormNoAccount(request.POST)
            if form.is_valid():
                jar = form.save(commit=False)
                jar.account = account
                jar.save()
                return redirect(reverse('account_detail', args=[account_id]))

    return render(request, 'core/account_detail.html', {
        'account': account,
        'jars': jars,
        'form': form,
        'jar_forms_dict': jar_forms_dict
    })


@login_required
def add_incoming_transaction(request, jar_id):
    jar = get_object_or_404(Jar, id=jar_id, account__created_by=request.user)
    
    if request.method == 'POST':
        form = IncomingTransactionForm(request.POST)
        if form.is_valid():
            transaction = form.save(commit=False)
            transaction.jar = jar
            transaction.created_by = request.user
            try:
                transaction.save()
                return redirect(reverse('account_detail', args=[jar.account.id]))
            except ValueError as e:
                form.add_error(None, str(e))
    else:
        form = IncomingTransactionForm()
    
    return render(request, 'core/add_transaction.html', {
        'form': form,
        'jar': jar,
        'transaction_type': 'incoming'
    })


@login_required
def add_outgoing_transaction(request, jar_id):
    jar = get_object_or_404(Jar, id=jar_id, account__created_by=request.user)
    
    if request.method == 'POST':
        form = OutgoingTransactionForm(request.POST, jar=jar)
        if form.is_valid():
            transaction = form.save(commit=False)
            transaction.jar = jar
            transaction.created_by = request.user
            try:
                transaction.save()
                return redirect(reverse('account_detail', args=[jar.account.id]))
            except ValueError as e:
                form.add_error(None, str(e))
    else:
        form = OutgoingTransactionForm(jar=jar)
    
    return render(request, 'core/add_transaction.html', {
        'form': form,
        'jar': jar,
        'transaction_type': 'outgoing'
    })


@login_required
def jar_transactions(request, jar_id):
    jar = get_object_or_404(Jar, id=jar_id, account__created_by=request.user)
    transactions = Transaction.objects.filter(jar=jar)
    
    return render(request, 'core/jar_transactions.html', {
        'jar': jar,
        'transactions': transactions
    })


@login_required
def all_transactions(request):
    # Get all transactions for the user's jars
    user_accounts = Account.objects.filter(created_by=request.user)
    user_jars = Jar.objects.filter(account__in=user_accounts)
    transactions = Transaction.objects.filter(jar__in=user_jars).select_related('jar', 'jar__account', 'jar__owner')
    
    # Get filter parameters
    account_filter = request.GET.get('account')
    jar_filter = request.GET.get('jar')
    transaction_type = request.GET.get('type')
    
    # Apply filters
    if account_filter:
        transactions = transactions.filter(jar__account_id=account_filter)
    if jar_filter:
        transactions = transactions.filter(jar_id=jar_filter)
    if transaction_type:
        transactions = transactions.filter(transaction_type=transaction_type)
    
    # Calculate summary statistics
    total_income = sum(t.amount for t in transactions if t.transaction_type == 'INCOMING')
    total_expenses = sum(t.amount for t in transactions if t.transaction_type == 'OUTGOING')
    net_amount = total_income - total_expenses
    
    context = {
        'transactions': transactions,
        'user_accounts': user_accounts,
        'user_jars': user_jars,
        'total_income': total_income,
        'total_expenses': total_expenses,
        'net_amount': net_amount,
        'account_filter': account_filter,
        'jar_filter': jar_filter,
        'transaction_type': transaction_type,
    }
    
    return render(request, 'core/all_transactions.html', context)
