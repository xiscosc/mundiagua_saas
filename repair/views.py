# -*- coding: utf-8 -*-
from itertools import chain
from operator import attrgetter

from async_messages import messages
from django.conf import settings
from django.core.paginator import Paginator
from django.urls import reverse_lazy
from django.db.models import Q
from django.http import HttpResponseRedirect
from django.views.generic import UpdateView, View

from core.models import SystemVariable
from core.utils import get_page_from_paginator
from core.views import SearchClientBaseView, CreateBaseView, TemplateView, PreSearchView
from intervention.models import Intervention
from repair.models import AthRepair, IdegisRepair, RepairStatus, ZodiacRepair, RepairType
from repair.utils import add_list_filters, generate_repair_qr_code, get_repair_view_by_type, get_repair_by_type, \
    add_repair_to_intervention, remove_repair_from_intervention, add_log_to_repair


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
        context['new_url3'] = "repair:repair-zodiac-new"
        context['btn_text3'] = "Crear reparación Fluidra"
        context['btn_class3'] = "btn-zodiac"
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
        return reverse_lazy('repair:repair-ath-view', kwargs={'pk': self.object.pk}) + "?=new1"


class CreateZodiacRepairView(CreateBaseView):
    model = ZodiacRepair
    fields = ['address', 'description', 'model', 'year', 'serial_number', 'notice_maker_number',
              'intern_description', 'warranty']

    def get_context_data(self, **kwargs):
        context = super(CreateZodiacRepairView, self).get_context_data(**kwargs)
        context['title'] = "Nueva reparación - FLUIDRA"
        context['subtitle'] = "Datos de la reparación"
        return context

    def get_success_url(self):
        return reverse_lazy('repair:repair-zodiac-view', kwargs={'pk': self.object.pk}) + "?=new1"


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
        return reverse_lazy('repair:repair-idegis-view', kwargs={'pk': self.object.pk}) + "?=new1"


class RepairView(UpdateView):
    context_object_name = "repair"
    template_name = "detail_repair.html"

    def get_context_data(self, **kwargs):
        context = super(RepairView, self).get_context_data(**kwargs)
        context['status'] = RepairStatus.objects.all()
        try:
            sms_text = SystemVariable.objects.get(key='repair_sms').get_value()
            context['sms_value'] = sms_text.replace(':id', context.get('object').__str__())
        except:
            pass
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


class ZodiacRepairView(RepairView):
    model = ZodiacRepair
    fields = ['description', 'model', 'year', 'serial_number', 'notice_maker_number',
              'intern_description', 'warranty']

    def get_success_url(self):
        return reverse_lazy('repair:repair-zodiac-view', kwargs={'pk': self.object.pk})


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
        type = RepairType(params.getlist('type_repair')[0])
        repair = get_repair_by_type(kwargs['pk'], type)
        log = add_log_to_repair(repair, st_id)
        repair.status_id = st_id
        repair.save()
        log.save()
        messages.success(self.request.user, "Cambio de estado realizado correctamente.")
        return HttpResponseRedirect(reverse_lazy(get_repair_view_by_type(type), kwargs={'pk': kwargs['pk']}))


class ListRepairView(TemplateView):
    template_name = "list_repair.html"

    def get_context_data(self, **kwargs):
        type = RepairType(kwargs['type'])
        starred = bool(int(kwargs['starred']))
        status_id = int(kwargs['status_id'])
        budget = int(kwargs['budget'])

        context = super(ListRepairView, self).get_context_data(**kwargs)
        page = int(self.request.GET.get('page', 1))
        context['list_navigation'] = True
        context['status'] = RepairStatus.objects.all()

        if type == RepairType.ALL:
            repairs_ath = add_list_filters(AthRepair, status_id, starred, budget)
            repairs_idegis = add_list_filters(IdegisRepair, status_id, starred, budget)
            repairs_zodiac = add_list_filters(ZodiacRepair, status_id, starred, budget)
            repairs = sorted(chain(repairs_ath, repairs_idegis, repairs_zodiac), key=attrgetter('date'), reverse=True)
        elif type == RepairType.ATH:
            repairs = add_list_filters(AthRepair, status_id, starred, budget)
            repairs = repairs.order_by("-date")
        elif type == RepairType.IDEGIS:
            repairs = add_list_filters(IdegisRepair, status_id, starred, budget)
            repairs = repairs.order_by("-date")
        elif type == RepairType.ZODIAC:
            repairs = add_list_filters(ZodiacRepair, status_id, starred, budget)
            repairs = repairs.order_by("-date")
        else:
            raise NotImplementedError()

        paginator = Paginator(repairs, settings.DEFAULT_NUM_PAGINATOR)
        context['repairs'] = get_page_from_paginator(paginator, page)
        return context


class PreSearchRepairView(PreSearchView):
    def set_data_and_response(self, request):
        search_text = self.search_text
        repairs_ath = AthRepair.objects.filter(Q(description__icontains=search_text) |
                                               Q(address__client__name__icontains=search_text) | Q(
            address__address__icontains=search_text) | Q(address__client__phones__phone__icontains=search_text) | Q(
            address__client__intern_code__icontains=search_text)).values_list('id', flat=True)
        repairs_idegis = IdegisRepair.objects.filter(Q(description__icontains=search_text) |
                                                     Q(address__client__name__icontains=search_text) | Q(
            address__address__icontains=search_text) | Q(address__client__phones__phone__icontains=search_text) | Q(
            address__client__intern_code__icontains=search_text)).values_list('id', flat=True)
        repairs_zodiac = ZodiacRepair.objects.filter(Q(description__icontains=search_text) |
                                                     Q(address__client__name__icontains=search_text) | Q(
            address__address__icontains=search_text) | Q(address__client__phones__phone__icontains=search_text) | Q(
            address__client__intern_code__icontains=search_text)).values_list('id', flat=True)
        request.session['search_repair_ath'] = list(repairs_ath)
        request.session['search_repair_idegis'] = list(repairs_idegis)
        request.session['search_repair_zodiac'] = list(repairs_zodiac)
        request.session['search_repair_text'] = search_text
        return HttpResponseRedirect(reverse_lazy('repair:repair-search', kwargs={'type': RepairType.ALL.value, 'starred': 0}))


class SearchRepairView(TemplateView):
    template_name = "list_repair.html"

    def get_context_data(self, **kwargs):
        context = super(SearchRepairView, self).get_context_data(**kwargs)
        page = int(self.request.GET.get('page', 1))
        search_text = str(self.request.session.get('search_repair_text', ""))
        context['title'] = "Búsqueda - " + search_text
        repairs_ath_pk = self.request.session.get('search_repair_ath', list())
        repairs_idegis_pk = self.request.session.get('search_repair_idegis', list())
        repairs_zodiac_pk = self.request.session.get('search_repair_zodiac', list())
        type = RepairType(kwargs['type'])
        starred = bool(int(kwargs['starred']))

        repairs_ath = AthRepair.objects.filter(pk__in=repairs_ath_pk)
        repairs_idegis = IdegisRepair.objects.filter(pk__in=repairs_idegis_pk)
        repairs_zodiac = ZodiacRepair.objects.filter(pk__in=repairs_zodiac_pk)
        if starred:
            repairs_ath = repairs_ath.filter(starred=True)
            repairs_idegis = repairs_idegis.filter(starred=True)
            repairs_zodiac = repairs_zodiac.filter(starred=True)

        if type == RepairType.ALL:
            repairs = sorted(chain(repairs_ath, repairs_idegis, repairs_zodiac), key=attrgetter('date'), reverse=True)
        elif type == RepairType.ATH:
            repairs = repairs_ath
        elif type == RepairType.IDEGIS:
            repairs = repairs_idegis
        elif type == RepairType.ZODIAC:
            repairs = repairs_zodiac
        else:
            raise NotImplementedError()

        paginator = Paginator(repairs, settings.DEFAULT_NUM_PAGINATOR)
        context['repairs'] = get_page_from_paginator(paginator, page)
        return context


class PrintRepairView(TemplateView):
    template_name = "print_repair.html"

    def get_context_data(self, **kwargs):
        context = super(PrintRepairView, self).get_context_data(**kwargs)
        try:
            context['repair_conditions'] = SystemVariable.objects.get(key='repair_conditions').get_value()
        except:
            pass

        context['repair'] = get_repair_by_type(kwargs['pk'], RepairType(self.kwargs['type']))
        context['qr'] = generate_repair_qr_code(context['repair'].online_id)
        return context


class ToggleStarredRepairView(View):
    def get(self, request, *args, **kwargs):
        repair = get_repair_by_type(kwargs['pk'], RepairType(self.kwargs['type']))
        repair.starred = not repair.starred
        repair.save()
        messages.success(self.request.user, "Cambio realizado correctamente")
        return HttpResponseRedirect(
            reverse_lazy(get_repair_view_by_type(RepairType(self.kwargs['type'])), kwargs={'pk': self.kwargs['pk']}))


class LinkInterventionView(View):
    def post(self, request, *args, **kwargs):
        import re
        params = request.POST.copy()
        type = RepairType(kwargs['type'])
        intervention_pk = int(re.sub("[^0-9]", "", params.getlist('intervention')[0]))

        try:
            intervention = Intervention.objects.get(pk=intervention_pk)
            add_repair_to_intervention(get_repair_by_type(kwargs['pk'], type), intervention)
            messages.success(self.request.user, "Avería V%d - %s vinculada correctamente." % (
                intervention_pk, intervention.address.client))

        except:

            messages.warning(self.request.user,
                             "No se ha podido vincular la avería V%d debido a un error, puede ser que el número sea incorrecto." % intervention_pk)

        return HttpResponseRedirect(reverse_lazy(get_repair_view_by_type(type), kwargs={'pk': kwargs['pk']}))


class UnlinkInterventionView(View):
    def get(self, request, *args, **kwargs):
        to_repair = bool(int(kwargs['to_repair']))
        intervention_pk = int(kwargs['pk_intervention'])
        type = RepairType(kwargs['type'])

        try:
            intervention = Intervention.objects.get(pk=intervention_pk)
            remove_repair_from_intervention(get_repair_by_type(kwargs['pk'], type), intervention)
            messages.success(self.request.user, "Avería V%d - %s desvinculada correctamente de la reparación." % (
                intervention_pk, intervention.address.client))

        except:
            messages.warning(self.request.user,
                             "No se ha podido desvincular la avería V%d debido a un error, puede ser que el número sea incorrecto." % intervention_pk)

        if to_repair:
            return HttpResponseRedirect(reverse_lazy(get_repair_view_by_type(type), kwargs={'pk': kwargs['pk']}))
        else:
            return HttpResponseRedirect(reverse_lazy('intervention:intervention-view', kwargs={'pk': intervention_pk}))
