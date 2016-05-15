# -*- coding: utf-8 -*-
from async_messages import message_user, constants
from django.core.urlresolvers import reverse_lazy
from django.http import HttpResponseRedirect
from django.views.generic import UpdateView, View

from core.views import SearchClientBaseView, CreateBaseView
from repair.models import AthRepair, IdegisRepair, RepairStatus, AthRepairLog, IdegisRepairLog


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
    fields = ['address', 'description', 'model', 'year', 'serial_number', 'notice_maker_number', 'description',
              'intern_description', 'warranty', "bypass", "connector", "transformer"]

    def get_context_data(self, **kwargs):
        context = super(CreateAthRepairView, self).get_context_data(**kwargs)
        context['title'] = "Nueva reparación - ATH"
        context['subtitle'] = "Datos de la reparación"
        return context

    def get_success_url(self):
        return reverse_lazy('repair-ath-view', kwargs={'pk': self.object.pk})


class CreateIdegisRepairView(CreateBaseView):
    model = IdegisRepair
    fields = ['address', 'description', 'model', 'year', 'serial_number', 'notice_maker_number', 'description',
              'intern_description', 'warranty', "ph", "orp", "electrode"]

    def get_context_data(self, **kwargs):
        context = super(CreateIdegisRepairView, self).get_context_data(**kwargs)
        context['title'] = "Nueva reparación - IDEGIS"
        context['subtitle'] = "Datos de la reparación"
        return context

    def get_success_url(self):
        return reverse_lazy('repair-idegis-view', kwargs={'pk': self.object.pk})


class RepairView(UpdateView):
    context_object_name = "repair"
    template_name = "detail_repair.html"

    def get_context_data(self, **kwargs):
        context = super(RepairView, self).get_context_data(**kwargs)
        context['status'] = RepairStatus.objects.all()
        return context

    def form_valid(self, form):
        message_user(self.request.user, "Reparación actualizada correctamente.", constants.SUCCESS)
        return super(RepairView, self).form_valid(form)


class AthRepairView(RepairView):
    model = AthRepair
    fields = ['description', 'model', 'year', 'serial_number', 'notice_maker_number', 'description',
              'intern_description', 'warranty', "bypass", "connector", "transformer"]

    def get_success_url(self):
        return reverse_lazy('repair-ath-view', kwargs={'pk': self.object.pk})


class IdegisRepairView(RepairView):
    model = IdegisRepair
    fields = ['description', 'model', 'year', 'serial_number', 'notice_maker_number', 'description',
              'intern_description', 'warranty', "ph", "orp", "electrode"]

    def get_success_url(self):
        return reverse_lazy('repair-idegis-view', kwargs={'pk': self.object.pk})


class UpdateStatusRepair(View):

    def post(self, request, *args, **kwargs):
        params = request.POST.copy()
        st_id = int(params.getlist('status_repair')[0])
        type = int(params.getlist('type_repair')[0])

        if type == 1:
            repair = AthRepair.objects.get(pk=kwargs['pk'])
            log = AthRepairLog(status_id=st_id, repair_id=kwargs['pk'])
            url = 'repair-ath-view'
        else:
            repair = IdegisRepair.objects.get(pk=kwargs['pk'])
            log = IdegisRepairLog(status_id=st_id, repair_id=kwargs['pk'])
            url = 'repair-idegis-view'
        repair.status_id = st_id
        repair.save()
        log.save()
        message_user(self.request.user, "Cambio de estado realizado correctamente.", constants.SUCCESS)
        return HttpResponseRedirect(reverse_lazy(url, kwargs={'pk': kwargs['pk']}))