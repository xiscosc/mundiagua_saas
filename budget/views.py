# -*- coding: utf-8 -*-
# Create your views here.
from budget.models import Budget
from core.views import SearchClientBaseView, CreateBaseView


class SearchClientView(SearchClientBaseView):

    def get_context_data(self, **kwargs):
        context = super(SearchClientView, self).get_context_data(**kwargs)
        context['title'] = "Nuevo presupuesto"
        context['new_url'] = "budget-budget-new"
        context['btn_text'] = "Crear presupuesto"
        context['btn_class'] = "btn-warning"
        return context


class CreateBudgetView(CreateBaseView):
    model = Budget
    fields = ['address', 'description', 'zone']
    template_name = "new_budget.html"