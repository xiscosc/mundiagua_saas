# -*- coding: utf-8 -*-
from async_messages import messages
from django.conf import settings
from django.core.paginator import Paginator
from django.urls import reverse_lazy
from django.db.models import Q
from django.http.response import HttpResponseRedirect
from django.views.generic import UpdateView
from django.views.generic.base import View, TemplateView

from core.models import SystemVariable
from core.utils import get_page_from_paginator
from core.views import SearchClientBaseView, CreateBaseView, PreSearchView
from engine.models import EngineRepair, EngineStatus, EngineRepairLog


class SearchClientView(SearchClientBaseView):
    def get_context_data(self, **kwargs):
        context = super(SearchClientView, self).get_context_data(**kwargs)
        context['title'] = "Nueva reparación de motor"
        context['new_url'] = "engine:engine-new"
        context['btn_text'] = "Crear reparación Motor"
        context['btn_class'] = "btn-success"
        return context


class CreateEngineRepairView(CreateBaseView):
    model = EngineRepair
    fields = ['address', 'description', 'model', 'year', 'serial_number', 'technical_service',
              'intern_description']

    def get_context_data(self, **kwargs):
        context = super(CreateEngineRepairView, self).get_context_data(**kwargs)
        context['title'] = "Nueva reparación de motor"
        context['subtitle'] = "Datos de la reparación"
        return context

    def get_success_url(self):
        return reverse_lazy('engine:engine-view', kwargs={'pk': self.object.pk})


class EngineRepairView(UpdateView):
    context_object_name = "repair"
    template_name = "detail_engine.html"
    model = EngineRepair
    fields = ['description', 'model', 'year', 'serial_number', 'technical_service', 'description',
              'intern_description']

    def get_success_url(self):
        return reverse_lazy('engine:engine-view', kwargs={'pk': self.object.pk})

    def get_context_data(self, **kwargs):
        context = super(EngineRepairView, self).get_context_data(**kwargs)
        context['status'] = EngineStatus.objects.all().order_by("pk")
        try:
            sms_text = SystemVariable.objects.get(key='enginerepair_sms').get_value()
            context['sms_value'] = sms_text.replace(':id', context.get('object').__str__())
        except:
            pass
        return context

    def form_valid(self, form):
        messages.success(self.request.user, "Reparación de motor actualizada correctamente.")
        return super(EngineRepairView, self).form_valid(form)


class UpdateStatusEngineRepair(View):
    def post(self, request, *args, **kwargs):
        params = request.POST.copy()
        st_id = int(params.getlist('status_repair')[0])
        repair = EngineRepair.objects.get(pk=kwargs['pk'])
        log = EngineRepairLog(status_id=st_id, repair_id=kwargs['pk'])
        repair.status_id = st_id
        repair.save()
        log.save()
        messages.success(self.request.user, "Cambio de estado realizado correctamente.")
        return HttpResponseRedirect(reverse_lazy("engine:engine-view", kwargs={'pk': kwargs['pk']}))


class PrintEngineRepairView(TemplateView):
    template_name = "print_engine.html"

    def get_context_data(self, **kwargs):
        context = super(PrintEngineRepairView, self).get_context_data(**kwargs)
        context['repair'] = EngineRepair.objects.get(pk=kwargs['pk'])
        try:
            context['repair_conditions'] = SystemVariable.objects.get(key='enginerepair_conditions').get_value()
        except:
            pass
        return context


class PreSearchEngineRepairView(PreSearchView):
    def set_data_and_response(self, request):
        search_text = self.search_text
        repairs = EngineRepair.objects.filter(
            Q(address__client__name__icontains=search_text) | Q(
                address__address__icontains=search_text) | Q(address__client__phones__phone__icontains=search_text) | Q(
                address__client__intern_code__icontains=search_text))

        pk_list = []
        for i in repairs:
            pk_list.append(i.pk)

        request.session['search_repairs_engine'] = pk_list
        request.session['search_repairs_engine_text'] = search_text
        return HttpResponseRedirect(reverse_lazy('engine:engine-search'))


class SearchEngineRepairView(TemplateView):
    template_name = "list_engine.html"

    def get_context_data(self, **kwargs):
        context = super(SearchEngineRepairView, self).get_context_data(**kwargs)
        page = int(self.request.GET.get('page', 1))
        search_text = str(self.request.session.get('search_repairs_engine_text', ""))
        context['title'] = "Búsqueda - " + search_text
        engines_pk = self.request.session.get('search_repairs_engine', list())
        repairs = EngineRepair.objects.filter(pk__in=engines_pk).order_by("-date")
        paginator = Paginator(repairs, settings.DEFAULT_NUM_PAGINATOR)
        context['repairs'] = get_page_from_paginator(paginator, page)
        return context


class ListEngineRepairView(TemplateView):
    template_name = "list_engine.html"

    def get_context_data(self, **kwargs):
        context = super(ListEngineRepairView, self).get_context_data(**kwargs)
        page = int(self.request.GET.get('page', 1))
        repairs = EngineRepair.objects.all().order_by("-date")
        paginator = Paginator(repairs, settings.DEFAULT_NUM_PAGINATOR)
        context['repairs'] = get_page_from_paginator(paginator, page)
        return context
