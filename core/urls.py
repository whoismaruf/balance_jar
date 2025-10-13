from django.urls import path
from . import views


urlpatterns = [
    path('', views.home, name='home'),
    path('owners/', views.owner_view, name='owner_view'),
    path('owners/<int:owner_id>/edit/', views.owner_view, name='owner_edit'),
    path('accounts/', views.account_view, name='account_view'),
    path('accounts/<int:account_id>/', views.account_detail_view, name='account_detail'),
    
    # Transaction URLs
    path('transactions/', views.all_transactions, name='all_transactions'),
    path('jars/<int:jar_id>/add-income/', views.add_incoming_transaction, name='add_incoming_transaction'),
    path('jars/<int:jar_id>/add-expense/', views.add_outgoing_transaction, name='add_outgoing_transaction'),
    path('jars/<int:jar_id>/transactions/', views.jar_transactions, name='jar_transactions'),
]