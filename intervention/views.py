# -*- coding: utf-8 -*-
import calendar
from datetime import date

from async_messages import message_user, constants
from django.conf import settings
from django.core.urlresolvers import reverse_lazy
from django.http import HttpResponseRedirect, JsonResponse, Http404
from django.views.generic import TemplateView, DetailView, View
from django.core.paginator import Paginator
from django.db.models import Q

from core.models import User
from core.views import SearchClientBaseView, CreateBaseView
from intervention.models import Intervention, Zone, InterventionStatus, InterventionModification, InterventionLog


class HomeView(TemplateView):
    template_name = 'home_intervention.html'

    def get_context_data(self, **kwargs):
        context = super(HomeView, self).get_context_data(**kwargs)
        context['status_pending'] = Intervention.objects.filter(status=1).count()
        context['status_assigned'] = Intervention.objects.filter(status=2).count()
        context['status_terminated'] = Intervention.objects.filter(status=3).count()
        context['status_cancelled'] = Intervention.objects.filter(status=4).count()
        context['modifications'] = InterventionModification.objects.all().order_by("-date")[:10]

        return context


class SearchClientView(SearchClientBaseView):
    def get_context_data(self, **kwargs):
        context = super(SearchClientView, self).get_context_data(**kwargs)
        context['title'] = "Nueva Avería"
        context['new_url'] = "intervention:intervention-new"
        context['btn_text'] = "Crear avería"
        context['btn_class'] = "btn-danger"
        return context


class CreateInterventionView(CreateBaseView):
    model = Intervention
    fields = ['address', 'description', 'zone']

    def get_context_data(self, **kwargs):
        context = super(CreateInterventionView, self).get_context_data(**kwargs)
        context['title'] = "Nueva avería"
        context['subtitle'] = "Datos de la avería"
        return context

    def get_success_url(self):
        return reverse_lazy('intervention:intervention-view', kwargs={'pk': self.object.pk})


class InterventionView(DetailView):
    model = Intervention
    context_object_name = "intervention"
    template_name = "detail_intervention.html"

    def get_context_data(self, **kwargs):
        context = super(InterventionView, self).get_context_data(**kwargs)
        context['zones'] = Zone.objects.all()
        context['users'] = User.objects.all()
        context['status'] = InterventionStatus.objects.all()
        return context


class UpdateInterventionView(View):
    def post(self, request, *args, **kwargs):
        params = request.POST.copy()
        intervention = Intervention.objects.get(pk=kwargs['pk'])
        intervention._old_status_id = intervention.status_id
        intervention._old_assigned_id = intervention.assigned_id
        intervention_save = True

        try:
            intervention.status_id = int(params.getlist('intervention_status')[0])
            if int(params.getlist('intervention_status')[0]) != settings.ASSIGNED_STATUS:
                intervention.assigned = None
            else:
                intervention.assigned_id = int(params.getlist('intervention_assigned')[0])
        except IndexError:
            pass

        try:
            intervention.zone_id = int(params.getlist('intervention_zone')[0])
        except IndexError:
            pass

        try:
            modification_text = params.getlist('intervention_modification')[0]
            modification = InterventionModification(intervention=intervention, note=modification_text,
                                                    created_by=request.user)
            modification.save()
            intervention_save = False
        except IndexError:
            pass

        try:
            user_to_send = User.objects.get(pk=int(params.getlist('user_to_send')[0]))
            intervention.send_to_user(user_to_send)
            intervention_save = False
        except IndexError:
            pass

        if intervention_save:
            intervention._current_user = request.user
            intervention.save()

        message_user(request.user, "Modificación realizada correctamente", constants.SUCCESS)
        return HttpResponseRedirect(reverse_lazy('intervention:intervention-view', kwargs={'pk': intervention.pk}))


class ListInterventionView(TemplateView):
    template_name = "list_intervention.html"

    def get_context_data(self, **kwargs):
        context = super(ListInterventionView, self).get_context_data(**kwargs)
        status_id = int(kwargs['intervention_status'])
        user_id = int(kwargs['user_assigned'])
        zone_id = int(kwargs['zone_assigned'])

        page = int(self.request.GET.get('page', 1))

        context['users'] = User.objects.all()
        context['zones'] = Zone.objects.all()
        context['list_navigation'] = True
        context['page'] = page

        self.request.session['list_status_id'] = status_id
        self.request.session['list_user_id'] = user_id
        self.request.session['list_zone_id'] = zone_id
        self.request.session['list_page'] = page

        interventions = Intervention.objects.filter(status=status_id).order_by("-date")
        try:
            context['search_status'] = InterventionStatus.objects.get(pk=status_id)
        except InterventionStatus.DoesNotExist:
            pass
        if user_id != 0:
            interventions = interventions.filter(assigned=user_id)
            try:
                context['search_user'] = User.objects.get(pk=user_id)
            except User.DoesNotExist:
                pass
        if zone_id != 0:
            interventions = interventions.filter(zone=zone_id)
            try:
                context['search_zone'] = Zone.objects.get(pk=zone_id)
            except Zone.DoesNotExist:
                pass

        paginator = Paginator(interventions, settings.DEFAULT_NUM_PAGINATOR)

        context['interventions'] = paginator.page(page)

        return context


class TerminateIntervention(TemplateView):
    template_name = "terminate_intervention.html"

    def get_context_data(self, **kwargs):
        context = super(TerminateIntervention, self).get_context_data(**kwargs)
        context['intervention'] = Intervention.objects.get(pk=int(kwargs['pk']))
        return context

    def post(self, request, *args, **kwargs):
        intervention = Intervention.objects.get(pk=kwargs['pk'])
        intervention._old_status_id = intervention.status_id
        intervention._old_assigned_id = intervention.assigned_id
        intervention._current_user = request.user
        intervention.assigned = None
        intervention.status_id = 3
        intervention.save()
        message_user(request.user, "Avería " + str(intervention) + " marcada como terminada", constants.SUCCESS)

        status_id = request.session.get('list_status_id', 1)
        user_id = request.session.get('list_user_id', 0)
        zone_id = request.session.get('list_zone_id', 0)
        page = request.session.get('list_page', 1)

        return HttpResponseRedirect(reverse_lazy('intervention:intervention-list',
                                                 kwargs={'intervention_status': status_id, 'zone': zone_id,
                                                         'user': user_id,}) + "?page=" + str(page))


class PreSearchInterventionView(View):
    def post(self, request, *args, **kwargs):
        params = request.POST.copy()
        search_text = params.getlist('search_text')[0]
        interventions = Intervention.objects.filter(Q(description__icontains=search_text) |
                                                    Q(address__client__name__icontains=search_text) | Q(
            address__address__icontains=search_text))
        pk_list = []
        for i in interventions:
            pk_list.append(i.pk)
        request.session['search_intervention'] = pk_list
        request.session['search_intervention_text'] = search_text
        return HttpResponseRedirect(reverse_lazy('intervention:intervention-search'))


class SearchInterventionView(TemplateView):
    template_name = "list_intervention.html"

    def get_context_data(self, **kwargs):
        context = super(SearchInterventionView, self).get_context_data(**kwargs)
        page = int(self.request.GET.get('page', 1))
        search_text = str(self.request.session.get('search_intervention_text', ""))
        context['title'] = "Búsqueda - " + search_text
        interventions_pk = self.request.session.get('search_intervention', list())
        interventions = Intervention.objects.filter(pk__in=interventions_pk)
        paginator = Paginator(interventions, settings.DEFAULT_NUM_PAGINATOR)
        context['interventions'] = paginator.page(page)
        return context


class ListModificationView(TemplateView):
    template_name = "list_modifications.html"

    def get_context_data(self, **kwargs):
        context = super(ListModificationView, self).get_context_data(**kwargs)
        page = int(self.request.GET.get('page', 1))
        modifications = InterventionModification.objects.all().order_by("-date")
        paginator = Paginator(modifications, settings.DEFAULT_MODIFICATIONS_PAGINATOR)
        context['modifications'] = paginator.page(page)
        return context


class MorrisView(View):
    def dispatch(self, request, *args, **kwargs):
        if not request.is_ajax():
            raise Http404("This is an ajax view, friend.")
        return super(MorrisView, self).dispatch(request, *args, **kwargs)


class MorrisInterventionAssigned(MorrisView):
    def get(self, request, *args, **kwargs):
        users = User.objects.all()
        data = []
        for u in users:
            logs = InterventionLog.objects.filter(assigned=u, date__month=date.today().month,
                                                  date__year=date.today().year).count()
            if logs > 0:
                data.append({"label": u.get_full_name(), "value": logs})
        return JsonResponse(data=data, safe=False)


class MorrisInterventionInput(MorrisView):
    def get(self, request, *args, **kwargs):
        data = []
        max_num = calendar.monthrange(date.today().year, date.today().month)[1].real
        for i in range(max_num):
            day = i + 1
            d = date(date.today().year, date.today().month, day)
            total = Intervention.objects.filter(date__day=day, date__year=d.year.real, date__month=d.month.real).count()
            data.append({'t': total, 'y': d.strftime("%Y-%m-%d")})
        return JsonResponse(data=data, safe=False)


class PrintInterventionView(DetailView):
    template_name = 'print_intervention.html'
    context_object_name = 'intervention'
    model = Intervention


class PrintListInterventionView(ListInterventionView):
    template_name = 'print_list_intervention.html'