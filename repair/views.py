# -*- coding: utf-8 -*-
from itertools import chain
from operator import attrgetter

from async_messages import messages
from django.conf import settings
from django.core.paginator import Paginator
from django.core.urlresolvers import reverse_lazy
from django.db.models import Q
from django.http import HttpResponseRedirect
from django.views.generic import UpdateView, View

from core.views import SearchClientBaseView, CreateBaseView, TemplateView, PreSearchView
from repair.models import AthRepair, IdegisRepair, RepairStatus, AthRepairLog, IdegisRepairLog


class SearchClientView(SearchClientBaseView):
    def get_context_data(self, **kwargs):
        context = super(SearchClientView, self).get_context_data(**kwargs)
        context['title'] = "Nueva reparación"
        context['new_url'] = "repair:repair-ath-new"
        context['btn_text'] = "Crear reparación ATH"
        context['btn_class'] = "btn-primary"
        context['new_url2'] = "repair:repair-idegis-new"
        context['btn_text2'] = "Crear reparación Idegis"
        context['btn_class2'] = "btn-default"
        return context


class CreateAthRepairView(CreateBaseView):
    model = AthRepair
    fields = ['address', 'description', 'model', 'year', 'serial_number', 'notice_maker_number',
              'intern_description', 'warranty', "bypass", "connector", "transformer"]

    def get_context_data(self, **kwargs):
        context = super(CreateAthRepairView, self).get_context_data(**kwargs)
        context['title'] = "Nueva reparación - ATH"
        context['subtitle'] = "Datos de la reparación"
        return context

    def get_success_url(self):
        return reverse_lazy('repair:repair-ath-view', kwargs={'pk': self.object.pk})


class CreateIdegisRepairView(CreateBaseView):
    model = IdegisRepair
    fields = ['address', 'description', 'model', 'year', 'serial_number', 'notice_maker_number',
              'intern_description', 'warranty', "ph", "orp", "electrode"]

    def get_context_data(self, **kwargs):
        context = super(CreateIdegisRepairView, self).get_context_data(**kwargs)
        context['title'] = "Nueva reparación - IDEGIS"
        context['subtitle'] = "Datos de la reparación"
        return context

    def get_success_url(self):
        return reverse_lazy('repair:repair-idegis-view', kwargs={'pk': self.object.pk})


class RepairView(UpdateView):
    context_object_name = "repair"
    template_name = "detail_repair.html"

    def get_context_data(self, **kwargs):
        context = super(RepairView, self).get_context_data(**kwargs)
        context['status'] = RepairStatus.objects.all()
        return context

    def form_valid(self, form):
        messages.success(self.request.user, "Reparación actualizada correctamente.")
        return super(RepairView, self).form_valid(form)


class AthRepairView(RepairView):
    model = AthRepair
    fields = ['description', 'model', 'year', 'serial_number', 'notice_maker_number',
              'intern_description', 'warranty', "bypass", "connector", "transformer"]

    def get_success_url(self):
        return reverse_lazy('repair:repair-ath-view', kwargs={'pk': self.object.pk})


class IdegisRepairView(RepairView):
    model = IdegisRepair
    fields = ['description', 'model', 'year', 'serial_number', 'notice_maker_number',
              'intern_description', 'warranty', "ph", "orp", "electrode"]

    def get_success_url(self):
        return reverse_lazy('repair:repair-idegis-view', kwargs={'pk': self.object.pk})


class UpdateStatusRepair(View):
    def post(self, request, *args, **kwargs):
        params = request.POST.copy()
        st_id = int(params.getlist('status_repair')[0])
        type = int(params.getlist('type_repair')[0])

        if type == 1:
            repair = AthRepair.objects.get(pk=kwargs['pk'])
            log = AthRepairLog(status_id=st_id, repair_id=kwargs['pk'])
            url = 'repair:repair-ath-view'
        else:
            repair = IdegisRepair.objects.get(pk=kwargs['pk'])
            log = IdegisRepairLog(status_id=st_id, repair_id=kwargs['pk'])
            url = 'repair:repair-idegis-view'
        repair.status_id = st_id
        repair.save()
        log.save()
        messages.success(self.request.user, "Cambio de estado realizado correctamente.")
        return HttpResponseRedirect(reverse_lazy(url, kwargs={'pk': kwargs['pk']}))


class ListRepairView(TemplateView):
    template_name = "list_repair.html"

    def get_context_data(self, **kwargs):
        context = super(ListRepairView, self).get_context_data(**kwargs)
        page = int(self.request.GET.get('page', 1))
        context['list_navigation'] = True
        type = int(kwargs['type'])

        if type == 0:
            repairs_ath = AthRepair.objects.all()
            repairs_idegis = IdegisRepair.objects.all()
            repairs = sorted(chain(repairs_ath, repairs_idegis), key=attrgetter('date'), reverse=True)
        elif type == 1:
            repairs = AthRepair.objects.all().order_by("-date")
        else:
            repairs = IdegisRepair.objects.all().order_by("-date")

        paginator = Paginator(repairs, settings.DEFAULT_NUM_PAGINATOR)
        context['repairs'] = paginator.page(page)
        return context


class PreSearchRepairView(PreSearchView):

    def set_data_and_response(self, request):
        params = request.POST.copy()
        search_text = params.getlist('search_text')[0]

        repairs_ath = AthRepair.objects.filter(Q(description__icontains=search_text) |
                                               Q(address__client__name__icontains=search_text) | Q(
            address__address__icontains=search_text))
        repairs_idegis = IdegisRepair.objects.filter(Q(description__icontains=search_text) |
                                                     Q(address__client__name__icontains=search_text) | Q(
            address__address__icontains=search_text))
        pk_list_ath = []
        pk_list_idegis = []
        for i in repairs_ath:
            pk_list_ath.append(i.pk)
        for i in repairs_idegis:
            pk_list_idegis.append(i.pk)
        request.session['search_repair_ath'] = pk_list_ath
        request.session['search_repair_idegis'] = pk_list_idegis
        request.session['search_repair_text'] = search_text
        return HttpResponseRedirect(reverse_lazy('repair:repair-search', kwargs={'type': 0}))


class SearchRepairView(TemplateView):
    template_name = "list_repair.html"

    def get_context_data(self, **kwargs):
        context = super(SearchRepairView, self).get_context_data(**kwargs)
        page = int(self.request.GET.get('page', 1))
        search_text = str(self.request.session.get('search_repair_text', ""))
        context['title'] = "Búsqueda - " + search_text
        repairs_ath_pk = self.request.session.get('search_repair_ath', list())
        repairs_idegis_pk = self.request.session.get('search_repair_idegis', list())
        type = int(kwargs['type'])

        if type == 0:
            repairs_ath = AthRepair.objects.filter(pk__in=repairs_ath_pk)
            repairs_idegis = IdegisRepair.objects.filter(pk__in=repairs_idegis_pk)
            repairs = sorted(chain(repairs_ath, repairs_idegis), key=attrgetter('date'), reverse=True)
        elif type == 1:
            repairs = AthRepair.objects.filter(pk__in=repairs_ath_pk).order_by("-date")
        else:
            repairs = IdegisRepair.objects.filter(pk__in=repairs_idegis_pk).order_by("-date")
        paginator = Paginator(repairs, settings.DEFAULT_NUM_PAGINATOR)
        context['repairs'] = paginator.page(page)
        return context


class PrintRepairView(TemplateView):
    template_name = "print_repair.html"

    def get_context_data(self, **kwargs):
        context = super(PrintRepairView, self).get_context_data(**kwargs)
        if int(kwargs['type']) == 1:
            context['repair'] = AthRepair.objects.get(pk=kwargs['pk'])
        else:
            context['repair'] = IdegisRepair.objects.get(pk=kwargs['pk'])
        return context