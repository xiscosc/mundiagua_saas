# -*- coding: utf-8 -*-
from django.views.generic import TemplateView

from budget.models import BudgetStandard, BudgetLineStandard
from core.views import SearchClientBaseView, CreateBaseView


class SearchClientView(SearchClientBaseView):

    def get_context_data(self, **kwargs):
        context = super(SearchClientView, self).get_context_data(**kwargs)
        context['title'] = "Nuevo presupuesto"
        context['new_url'] = "budget:budget-new"
        context['btn_text'] = "Crear presupuesto"
        context['btn_class'] = "btn-warning"
        return context


class CreateBudgetView(CreateBaseView):
    model = BudgetStandard
    fields = ['address', 'introduction', 'conditions', 'tax']

    def get_context_data(self, **kwargs):
        context = super(CreateBudgetView, self).get_context_data(**kwargs)
        context['title'] = "Nuevo presupuesto"
        context['subtitle'] = "Datos del presupuesto"
        return context


class CreateLineBudgetView(TemplateView):
    template_name = "lines_budget.html"
