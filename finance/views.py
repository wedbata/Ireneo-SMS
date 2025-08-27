from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from accounts.decorators import admin_required, finance_required
from django.utils.decorators import method_decorator

from .models import Expense, ExpenseCategory
from .forms import ExpenseForm, ExpenseCategoryForm

def index(request):
    return render(request, 'finance/index.html', {'title': 'Finance'})

@method_decorator(finance_required, name='dispatch')
class ExpenseListView(LoginRequiredMixin, ListView):
    model = Expense
    template_name = 'finance/expense_list.html'
    context_object_name = 'expenses'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Expenses'
        return context

@method_decorator(finance_required, name='dispatch')
class ExpenseCreateView(LoginRequiredMixin, CreateView):
    model = Expense
    form_class = ExpenseForm
    template_name = 'finance/expense_form.html'
    success_url = reverse_lazy('finance:expense_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Create Expense'
        return context

@method_decorator(finance_required, name='dispatch')
class ExpenseUpdateView(LoginRequiredMixin, UpdateView):
    model = Expense
    form_class = ExpenseForm
    template_name = 'finance/expense_form.html'
    success_url = reverse_lazy('finance:expense_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Update Expense'
        return context

@method_decorator(finance_required, name='dispatch')
class ExpenseDeleteView(LoginRequiredMixin, DeleteView):
    model = Expense
    template_name = 'finance/expense_confirm_delete.html'
    success_url = reverse_lazy('finance:expense_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Delete Expense'
        return context

@method_decorator(admin_required, name='dispatch')
class ExpenseCategoryListView(LoginRequiredMixin, ListView):
    model = ExpenseCategory
    template_name = 'finance/expense_category_list.html'
    context_object_name = 'categories'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Expense Categories'
        return context

@method_decorator(admin_required, name='dispatch')
class ExpenseCategoryCreateView(LoginRequiredMixin, CreateView):
    model = ExpenseCategory
    form_class = ExpenseCategoryForm
    template_name = 'finance/expense_category_form.html'
    success_url = reverse_lazy('finance:expense_category_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Create Expense Category'
        return context

@method_decorator(admin_required, name='dispatch')
class ExpenseCategoryUpdateView(LoginRequiredMixin, UpdateView):
    model = ExpenseCategory
    form_class = ExpenseCategoryForm
    template_name = 'finance/expense_category_form.html'
    success_url = reverse_lazy('finance:expense_category_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Update Expense Category'
        return context

@method_decorator(admin_required, name='dispatch')
class ExpenseCategoryDeleteView(LoginRequiredMixin, DeleteView):
    model = ExpenseCategory
    template_name = 'finance/expense_category_confirm_delete.html'
    success_url = reverse_lazy('finance:expense_category_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Delete Expense Category'
        return context