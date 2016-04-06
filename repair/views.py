# -*- coding: utf-8 -*-
from core.views import SearchClientBaseView, CreateBaseView
from repair.models import AthRepair, IdegisRepair


class SearchClientView(SearchClientBaseView):

    def get_context_data(self, **kwargs):
        context = super(SearchClientView, self).get_context_data(**kwargs)
        context['title'] = "Nueva reparación"
        context['new_url'] = "repair-ath-new"
        context['btn_text'] = "Crear reparación ATH"
        context['btn_class'] = "btn-primary"
        context['new_url2'] = "repair-idegis-new"
        context['btn_text2'] = "Crear reparación Idegis"
        context['btn_class2'] = "btn-default"
        return context


class CreateAthRepairView(CreateBaseView):
    model = AthRepair
    fields = ['address', 'description', 'zone']
    template_name = "new_budget.html"


class CreateIdegisRepairView(CreateBaseView):
    model = IdegisRepair
    fields = ['address', 'description', 'zone']
    template_name = "new_budget.html"