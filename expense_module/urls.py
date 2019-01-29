from django.urls import path
from .views import *

urlpatterns = [
    path('addNewExpense', add_new_expense, name='addNewExpense'),
    path('processReceipt', process_receipt, name='processReceipt'), 
    path('viewReceipt/<int:receipt_id>/', view_receipt, name='viewReceipt'),
    path('deleteReceipt/<int:receipt_id>/', delete_receipt, name='deleteReceipt'),
    path('test', test, name='expense_test'),
    
]   