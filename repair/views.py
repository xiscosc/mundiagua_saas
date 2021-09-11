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
from repair.models import AthRepair, IdegisRepair, RepairStatus, AthRepairLog, IdegisRepairLog
from repair.tasks import send_sms_tracking
from repair.utils import add_list_filters
from core.tasks import send_mail_client


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
        return reverse_lazy('repair:repair-ath-view', kwargs={'pk': self.object.pk}) + "?=new1"


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
        type = int(kwargs['type'])
        starred = bool(int(kwargs['starred']))
        status_id = int(kwargs['status_id'])
        budget = int(kwargs['budget'])

        context = super(ListRepairView, self).get_context_data(**kwargs)
        page = int(self.request.GET.get('page', 1))
        context['list_navigation'] = True
        context['status'] = RepairStatus.objects.all()

        if type == 0:
            repairs_ath = add_list_filters(AthRepair, status_id, starred, budget)
            repairs_idegis = add_list_filters(IdegisRepair, status_id, starred, budget)
            repairs = sorted(chain(repairs_ath, repairs_idegis), key=attrgetter('date'), reverse=True)
        elif type == 1:
            repairs = add_list_filters(AthRepair, status_id, starred, budget)
            repairs = repairs.order_by("-date")
        else:
            repairs = add_list_filters(IdegisRepair, status_id, starred, budget)
            repairs = repairs.order_by("-date")

        paginator = Paginator(repairs, settings.DEFAULT_NUM_PAGINATOR)
        context['repairs'] = get_page_from_paginator(paginator, page)
        return context


class PreSearchRepairView(PreSearchView):
    def set_data_and_response(self, request):
        search_text = self.search_text
        repairs_ath = AthRepair.objects.filter(Q(description__icontains=search_text) |
                                               Q(address__client__name__icontains=search_text) | Q(
            address__address__icontains=search_text) | Q(address__client__phones__phone__icontains=search_text) | Q(
            address__client__intern_code__icontains=search_text))
        repairs_idegis = IdegisRepair.objects.filter(Q(description__icontains=search_text) |
                                                     Q(address__client__name__icontains=search_text) | Q(
            address__address__icontains=search_text) | Q(address__client__phones__phone__icontains=search_text) | Q(
            address__client__intern_code__icontains=search_text))
        pk_list_ath = []
        pk_list_idegis = []
        for i in repairs_ath:
            pk_list_ath.append(i.pk)
        for i in repairs_idegis:
            pk_list_idegis.append(i.pk)
        request.session['search_repair_ath'] = pk_list_ath
        request.session['search_repair_idegis'] = pk_list_idegis
        request.session['search_repair_text'] = search_text
        return HttpResponseRedirect(reverse_lazy('repair:repair-search', kwargs={'type': 0, 'starred': 0}))


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
        starred = bool(int(kwargs['starred']))

        if type == 0:
            repairs_ath = AthRepair.objects.filter(pk__in=repairs_ath_pk)
            repairs_idegis = IdegisRepair.objects.filter(pk__in=repairs_idegis_pk)
            if starred:
                repairs_ath = repairs_ath.filter(starred=True)
                repairs_idegis = repairs_idegis.filter(starred=True)
            repairs = sorted(chain(repairs_ath, repairs_idegis), key=attrgetter('date'), reverse=True)
        elif type == 1:
            repairs = AthRepair.objects.filter(pk__in=repairs_ath_pk).order_by("-date")
            if starred:
                repairs = repairs.filter(starred=True)
        else:
            repairs = IdegisRepair.objects.filter(pk__in=repairs_idegis_pk).order_by("-date")
            if starred:
                repairs = repairs.filter(starred=True)
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
        if int(kwargs['type']) == 1:
            context['repair'] = AthRepair.objects.get(pk=kwargs['pk'])
        else:
            context['repair'] = IdegisRepair.objects.get(pk=kwargs['pk'])
        return context


class ToggleStarredRepairView(View):
    def get(self, request, *args, **kwargs):
        if int(self.kwargs['type']) == 1:
            urlname = 'repair-ath-view'
            repair = AthRepair.objects.get(pk=self.kwargs['pk'])
        else:
            urlname = 'repair-idegis-view'
            repair = IdegisRepair.objects.get(pk=self.kwargs['pk'])
        repair.starred = not repair.starred
        repair.save()
        messages.success(self.request.user, "Cambio realizado correctamente")
        return HttpResponseRedirect(reverse_lazy("repair:" + urlname, kwargs={'pk': self.kwargs['pk']}))


class LinkInterventionView(View):
    def post(self, request, *args, **kwargs):
        import re
        params = request.POST.copy()
        type = bool(int(kwargs['type']))
        intervention_pk = int(re.sub("[^0-9]", "", params.getlist('intervention')[0]))

        try:
            intervention = Intervention.objects.get(pk=intervention_pk)

            if type:
                repair = AthRepair.objects.get(pk=kwargs['pk'])
                intervention.repairs_ath.add(repair)
                url = 'repair:repair-ath-view'
            else:
                repair = IdegisRepair.objects.get(pk=kwargs['pk'])
                intervention.repairs_idegis.add(repair)
                url = 'repair:repair-idegis-view'

            messages.success(self.request.user, "Avería V%d - %s vinculada correctamente." % (
                intervention_pk, intervention.address.client))

        except:
            if type:
                url = 'repair:repair-ath-view'
            else:
                url = 'repair:repair-idegis-view'

            messages.warning(self.request.user,
                             "No se ha podido vincular la avería V%d debido a un error, puede ser que el número sea incorrecto." % intervention_pk)

        return HttpResponseRedirect(reverse_lazy(url, kwargs={'pk': kwargs['pk']}))


class UnlinkInterventionView(View):
    def get(self, request, *args, **kwargs):
        type = bool(int(kwargs['type']))
        to_repair = bool(int(kwargs['to_repair']))
        intervention_pk = int(kwargs['pk_intervention'])

        try:
            intervention = Intervention.objects.get(pk=intervention_pk)

            if type:
                repair = AthRepair.objects.get(pk=kwargs['pk'])
                intervention.repairs_ath.remove(repair)
                url = 'repair:repair-ath-view'
            else:
                repair = IdegisRepair.objects.get(pk=kwargs['pk'])
                intervention.repairs_idegis.remove(repair)
                url = 'repair:repair-idegis-view'

            messages.success(self.request.user, "Avería V%d - %s desvinculada correctamente de la reparación." % (
                intervention_pk, intervention.address.client))

        except:
            if type:
                url = 'repair:repair-ath-view'
            else:
                url = 'repair:repair-idegis-view'

            messages.warning(self.request.user,
                             "No se ha podido desvincular la avería V%d debido a un error, puede ser que el número sea incorrecto." % intervention_pk)

        if to_repair:
            return HttpResponseRedirect(reverse_lazy(url, kwargs={'pk': kwargs['pk']}))
        else:
            return HttpResponseRedirect(reverse_lazy('intervention:intervention-view', kwargs={'pk': intervention_pk}))


class SendTrackingRepairView(View):
    def post(self, request, *args, **kwargs):
        params = request.POST.copy()
        type = int(params.getlist('type_repair')[0])
        sending_something = False

        if type == 1:
            repair = AthRepair.objects.get(pk=kwargs['pk'])
            url = 'repair:repair-ath-view'
        else:
            repair = IdegisRepair.objects.get(pk=kwargs['pk'])
            url = 'repair:repair-idegis-view'

        if params.getlist('send_sms', "off")[0] == "on":
            phone_pk = int(params.getlist('phone_id', "0")[0])
            if phone_pk != 0:
                send_sms_tracking(repair.pk, type, phone_pk, request.user.pk)
                sending_something = True

        if params.getlist('send_email', "off")[0] == "on":
            email_pk = int(params.getlist('email_id', "0")[0])
            if email_pk != 0:
                from client.models import Email
                email = Email.objects.get(pk=email_pk)
                if email.client.pk == repair.address.client.pk:
                    sending_something = True
                    url_body = "https://customerservice.mundiaguabalear.com/?id=" + repair.online_id
                    subject = u'Reparación %s registrada' % repair.__str__()
                    body = u'Su reparación %s ha sido registrada con éxito, puede consultar su estado ' \
                           u'en el siguiente enlace %s, si no le funciona el enlace cópielo y péguelo en su navegador.' \
                           u'\n\nTambién puede visitar nuestra web ' \
                           u'www.mundiaguabalear.com con el id de reparación ' \
                           u'%s.\n\nQuedamos a su disposición para cualquier duda o ' \
                           u'consulta.' % (repair.__str__(), url_body, repair.online_id)

                    send_mail_client(email_pk, subject, body, request.user.pk)

        if sending_something:
            messages.success(self.request.user, "Se han notificado los datos de seguimiento al cliente.")
        else:
            messages.warning(self.request.user, "No se ha notificado nada al cliente.")
        return HttpResponseRedirect(reverse_lazy(url, kwargs={'pk': kwargs['pk']}))
