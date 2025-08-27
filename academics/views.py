from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from accounts.decorators import admin_required
from django.utils.decorators import method_decorator

from .models import Subject
from .forms import SubjectForm

def index(request):
    return render(request, 'academics/index.html', {'title': 'Academics'})

@method_decorator(admin_required, name='dispatch')
class SubjectListView(LoginRequiredMixin, ListView):
    model = Subject
    template_name = 'academics/subject_list.html'
    context_object_name = 'subjects'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Subjects'
        return context

@method_decorator(admin_required, name='dispatch')
class SubjectCreateView(LoginRequiredMixin, CreateView):
    model = Subject
    form_class = SubjectForm
    template_name = 'academics/subject_form.html'
    success_url = reverse_lazy('academics:subject_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Create Subject'
        return context

@method_decorator(admin_required, name='dispatch')
class SubjectUpdateView(LoginRequiredMixin, UpdateView):
    model = Subject
    form_class = SubjectForm
    template_name = 'academics/subject_form.html'
    success_url = reverse_lazy('academics:subject_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Update Subject'
        return context

@method_decorator(admin_required, name='dispatch')
class SubjectDeleteView(LoginRequiredMixin, DeleteView):
    model = Subject
    template_name = 'academics/subject_confirm_delete.html'
    success_url = reverse_lazy('academics:subject_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Delete Subject'
        return context
