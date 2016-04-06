# -*- coding: utf-8 -*-
from django.views.generic import TemplateView

from core.views import SearchClientBaseView


class HomeView(TemplateView):
    template_name = 'home.html'


class SearchClientView(SearchClientBaseView):

    def get_context_data(self, **kwargs):
        context = super(SearchClientView, self).get_context_data(**kwargs)
        context['title'] = "Nueva Avería"
        context['new_url'] = "client-client"
        context['btn_text'] = "Crear avería"
        context['btn_class'] = "btn-danger"
        return context