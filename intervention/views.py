# -*- coding: utf-8 -*-
from django.views.generic import TemplateView, DetailView

from client.models import Phone
from core.views import SearchClientBaseView, CreateBaseView
from intervention.models import Intervention


class HomeView(TemplateView):
    template_name = 'home.html'


class SearchClientView(SearchClientBaseView):

    def get_context_data(self, **kwargs):
        context = super(SearchClientView, self).get_context_data(**kwargs)
        context['title'] = "Nueva Avería"
        context['new_url'] = "intervention-intervention-new"
        context['btn_text'] = "Crear avería"
        context['btn_class'] = "btn-danger"
        return context


class CreateInterventionView(CreateBaseView):
    model = Intervention
    fields = ['address', 'description', 'zone']
    template_name = "new_intervention.html"


class InterventionView(DetailView):
    model = Intervention
    context_object_name = "intervention"
    template_name = "detail_intervention.html"

