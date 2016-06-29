# -*- coding: utf-8 -*-
from django.conf import settings
from django.core.urlresolvers import reverse_lazy
from django.http import HttpResponseRedirect, JsonResponse, Http404
from django.views.generic import TemplateView, DetailView, View
from django.core.paginator import Paginator
from django.db.models import Q

from core.models import User
from core.views import SearchClientBaseView, CreateBaseView
from intervention.models import Intervention, Zone, InterventionStatus, InterventionModification
from intervention.utils import update_intervention, generate_data_year_vs, generate_data_intervention_input, \
    generate_data_intervention_assigned, terminate_intervention, get_intervention_list


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
        context['users'] = User.objects.filter(is_active=True).order_by("order")
        context['status'] = InterventionStatus.objects.all()
        return context


class UpdateInterventionView(View):

    def post(self, request, *args, **kwargs):
        update_intervention(kwargs['pk'], request)
        return HttpResponseRedirect(reverse_lazy('intervention:intervention-view', kwargs={'pk': kwargs['pk']}))


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

        list_data = get_intervention_list(status_id, user_id, zone_id)
        context['search_status'] = list_data['search_status']
        context['search_user'] = list_data['search_user']
        context['search_zone'] = list_data['search_zone']

        paginator = Paginator(list_data['interventions'], settings.DEFAULT_NUM_PAGINATOR)

        context['interventions'] = paginator.page(page)

        return context


class TerminateIntervention(TemplateView):
    template_name = "terminate_intervention.html"

    def get_context_data(self, **kwargs):
        context = super(TerminateIntervention, self).get_context_data(**kwargs)
        context['intervention'] = Intervention.objects.get(pk=int(kwargs['pk']))
        return context

    def post(self, request, *args, **kwargs):
        terminate_intervention(kwargs['pk'], request)
        status_id = request.session.get('list_status_id', 1)
        user_id = request.session.get('list_user_id', 0)
        zone_id = request.session.get('list_zone_id', 0)
        page = request.session.get('list_page', 1)

        return HttpResponseRedirect(reverse_lazy('intervention:intervention-list',
                                                 kwargs={'intervention_status': status_id, 'zone_assigned': zone_id,
                                                         'user_assigned': user_id}) + "?page=" + str(page))


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
        return JsonResponse(data=generate_data_intervention_assigned(), safe=False)


class MorrisInterventionInput(MorrisView):

    def get(self, request, *args, **kwargs):
        return JsonResponse(data=generate_data_intervention_input(), safe=False)


class MorrisYearVs(MorrisView):

    def get(self, request, *args, **kwargs):
        return JsonResponse(data=generate_data_year_vs(), safe=False)


class PrintInterventionView(DetailView):
    template_name = 'print_intervention.html'
    context_object_name = 'intervention'
    model = Intervention


class PrintListInterventionView(ListInterventionView):
    template_name = 'print_list_intervention.html'


class OwnListInterventionView(TemplateView):
    template_name = 'list_intervention.html'

    def get_context_data(self, **kwargs):
        context = super(OwnListInterventionView, self).get_context_data(**kwargs)
        page = int(self.request.GET.get('page', 1))
        context['page'] = page
        interventions = Intervention.objects.filter(status=settings.ASSIGNED_STATUS, assigned=self.request.user).order_by("-date")
        paginator = Paginator(interventions, settings.DEFAULT_NUM_PAGINATOR)
        context['interventions'] = paginator.page(page)

        return context
