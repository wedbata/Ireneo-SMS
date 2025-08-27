from django.urls import path
from . import views

app_name = 'finance'

urlpatterns = [
    path('', views.index, name='index'),
    path('expenses/', views.ExpenseListView.as_view(), name='expense_list'),
    path('expenses/create/', views.ExpenseCreateView.as_view(), name='expense_create'),
    path('expenses/<int:pk>/update/', views.ExpenseUpdateView.as_view(), name='expense_update'),
    path('expenses/<int:pk>/delete/', views.ExpenseDeleteView.as_view(), name='expense_delete'),
    path('categories/', views.ExpenseCategoryListView.as_view(), name='expense_category_list'),
    path('categories/create/', views.ExpenseCategoryCreateView.as_view(), name='expense_category_create'),
    path('categories/<int:pk>/update/', views.ExpenseCategoryUpdateView.as_view(), name='expense_category_update'),
    path('categories/<int:pk>/delete/', views.ExpenseCategoryDeleteView.as_view(), name='expense_category_delete'),
]
