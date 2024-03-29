# -*- coding: utf-8 -*-
from datetime import date
from django.conf import settings
from django.urls import reverse_lazy
from django.http import (
    HttpResponseRedirect,
    JsonResponse,
    Http404,
    QueryDict,
)
from django.views.generic import TemplateView, DetailView, View, UpdateView
from django.core.paginator import Paginator
from django.db.models import Q
from async_messages import messages

from core.files.utils import get_items_in_json_response, store_file_metadata_from_post, delete_file_metadata, \
    get_file_metadata, get_file_download_url, update_file_metadata
from core.models import User, SystemVariable
from core.views import SearchClientBaseView, CreateBaseView, PreSearchView
from core.utils import (
    ATH_REGEX,
    IDEGIS_REGEX,
    BUDGET_REGEX,
    BUDGET_REGEX_2ND_FORMAT,
    BUDGET_REGEX_3RD_FORMAT,
    get_page_from_paginator,
    ZODIAC_REGEX,
)
from intervention.models import (
    Intervention,
    Zone,
    InterventionStatus,
    InterventionModification,
    InterventionSubStatus,
    InterventionLogSub,
    Tag,
)
from intervention.utils import (
    update_intervention,
    generate_data_year_vs,
    generate_data_intervention_input,
    generate_data_intervention_assigned,
    terminate_intervention,
    get_intervention_list,
    bill_intervention,
    generate_report,
)
from intervention.forms import (
    NewInterventionForm,
    EarlyInterventionModificationForm,
    InterventionModificationForm,
)
from repair.models import RepairType


class HomeView(TemplateView):
    template_name = "home_intervention.html"

    def get_interventions(self):
        inter = Intervention.objects.filter(status_id=2)
        inter_result = []
        for i in inter:
            if i.address.get_geo():
                inter_result.append(i)
        return inter_result

    def get_context_data(self, **kwargs):
        context = super(HomeView, self).get_context_data(**kwargs)
        context["status_pending"] = Intervention.objects.filter(status=1).count()
        context["status_assigned"] = Intervention.objects.filter(status=2).count()
        context["status_terminated"] = Intervention.objects.filter(status=3).count()
        context["status_cancelled"] = Intervention.objects.filter(status=4).count()
        context["status_preparation"] = Intervention.objects.filter(status=5).count()
        context["modifications"] = InterventionModification.objects.all().order_by(
            "-date"
        )[:15]
        context["months"] = [x for x in range(1, 13)]
        context["years"] = [x for x in range(2014, date.today().year + 1)]
        context["interventions"] = self.get_interventions()
        context["gmaps_api"] = settings.GMAPS_API_KEY
        context["zones"] = Zone.objects.all().order_by("pk")
        context["tags"] = Tag.objects.all().order_by("pk")
        context["users"] = User.objects.all()
        return context


class SearchClientView(SearchClientBaseView):
    def get_context_data(self, **kwargs):
        context = super(SearchClientView, self).get_context_data(**kwargs)
        context["title"] = "Nueva Avería"
        context["new_url"] = "intervention:intervention-new"
        context["btn_text"] = "Crear avería"
        context["btn_class"] = "btn-danger"
        return context


class CreateInterventionView(CreateBaseView):
    model = Intervention
    form_class = NewInterventionForm

    def get_context_data(self, **kwargs):
        context = super(CreateInterventionView, self).get_context_data(**kwargs)
        context["title"] = "Nueva avería"
        context["subtitle"] = "Datos de la avería"
        context["zones"] = Zone.objects.all()
        return context

    def get_success_url(self):
        return reverse_lazy(
            "intervention:intervention-view", kwargs={"pk": self.object.pk}
        )


class InterventionView(DetailView):
    model = Intervention
    context_object_name = "intervention"
    template_name = "detail_intervention.html"

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_officer:
            return super(InterventionView, self).dispatch(request, *args, **kwargs)
        else:
            try:
                intervention = Intervention.objects.get(pk=kwargs["pk"])
                if (
                        intervention.status_id == 2
                        and intervention.assigned_id == request.user.id
                ):
                    return super(InterventionView, self).dispatch(
                        request, *args, **kwargs
                    )
                else:
                    return HttpResponseRedirect(
                        reverse_lazy("intervention:intervention-forbidden")
                    )
            except:
                return HttpResponseRedirect(
                    reverse_lazy("intervention:intervention-forbidden")
                )

    def get_context_data(self, **kwargs):
        context = super(InterventionView, self).get_context_data(**kwargs)
        context["zones"] = Zone.objects.all().exclude(pk=9).order_by("pk")
        context["users"] = User.objects.filter(is_active=True).order_by("order_in_app")
        allowed_transition_ids = self.get_object().status.allowed_transition_ids
        context["show_users"] = 2 in allowed_transition_ids
        context["status"] = InterventionStatus.objects.filter(
            pk__in=allowed_transition_ids
        )
        context["sub_status"] = InterventionSubStatus.objects.all()
        try:
            context["sms_value"] = SystemVariable.objects.get(
                key="intervention_sms"
            ).get_value()
        except:
            pass
        return context


class UpdateInterventionView(View):
    def post(self, request, *args, **kwargs):
        update_intervention(kwargs["pk"], request)
        return HttpResponseRedirect(
            reverse_lazy("intervention:intervention-view", kwargs={"pk": kwargs["pk"]})
        )


class EditInterventionView(UpdateView):
    model = Intervention
    template_name = "edit_intervention.html"

    def get_form_class(self):
        if self.object.is_early_modifiable():
            return EarlyInterventionModificationForm
        else:
            return InterventionModificationForm

    def get_success_url(self):
        messages.success(
            self.request.user, "Datos de la avería actualizados correctamente"
        )
        return reverse_lazy(
            "intervention:intervention-view", kwargs={"pk": self.kwargs["pk"]}
        )


class ListInterventionView(TemplateView):
    template_name = "list_intervention.html"

    def get_context_data(self, **kwargs):
        context = super(ListInterventionView, self).get_context_data(**kwargs)
        status_id = int(kwargs["intervention_status"])
        user_id = int(kwargs["user_assigned"])
        zone_id = int(kwargs["zone_assigned"])
        starred = int(kwargs["starred"])
        tag_id = int(kwargs["tag_assigned"])

        page = int(self.request.GET.get("page", 1))

        context["users"] = User.objects.all()
        context["zones"] = Zone.objects.all().order_by("pk")
        context["tags"] = Tag.objects.all()
        context["list_navigation"] = True
        context["starred"] = starred
        context["page"] = page

        self.request.session["list_status_id"] = status_id
        self.request.session["list_user_id"] = user_id
        self.request.session["list_zone_id"] = zone_id
        self.request.session["list_tag_id"] = tag_id
        self.request.session["list_page"] = page
        self.request.session["list_starred"] = starred

        list_data = get_intervention_list(status_id, user_id, zone_id, starred, tag_id)
        context["search_status"] = list_data["search_status"]
        context["search_user"] = list_data["search_user"]
        context["search_zone"] = list_data["search_zone"]
        context["search_tag"] = list_data["search_tag"]

        elements_per_page = settings.DEFAULT_INTERVENTION_PAGINATOR
        if not self.request.user_agent.is_pc:
            elements_per_page = settings.DEFAULT_NUM_PAGINATOR
        paginator = Paginator(list_data["interventions"], elements_per_page)

        context["interventions"] = get_page_from_paginator(paginator, page)

        return context


class FastModifyIntervention(TemplateView):
    def get_context_data(self, **kwargs):
        context = super(FastModifyIntervention, self).get_context_data(**kwargs)
        context["intervention"] = Intervention.objects.get(pk=int(kwargs["pk"]))
        return context

    def make_modifications(self, pk, request):
        pass

    def post(self, request, *args, **kwargs):
        self.make_modifications(kwargs["pk"], request)
        status_id = request.session.get("list_status_id", 1)
        user_id = request.session.get("list_user_id", 0)
        zone_id = request.session.get("list_zone_id", 0)
        tag_id = request.session.get("list_tag_id", 0)
        page = request.session.get("list_page", 1)
        starred = request.session.get("list_starred", 0)

        return HttpResponseRedirect(
            reverse_lazy(
                "intervention:intervention-list",
                kwargs={
                    "intervention_status": status_id,
                    "zone_assigned": zone_id,
                    "user_assigned": user_id,
                    "starred": starred,
                    "tag_assigned": tag_id,
                },
            )
            + "?page="
            + str(page)
        )


class TerminateIntervention(FastModifyIntervention):
    template_name = "terminate_intervention.html"

    def make_modifications(self, pk, request):
        terminate_intervention(pk, request)


class BillIntervention(FastModifyIntervention):
    template_name = "bill_intervention.html"

    def make_modifications(self, pk, request):
        bill_intervention(pk, request)


class PreSearchInterventionView(PreSearchView):
    def set_data_and_response(self, request):
        search_text = self.search_text
        interventions = Intervention.objects.filter(
            Q(description__icontains=search_text)
            | Q(short_description__icontains=search_text)
            | Q(address__client__phones__phone__icontains=search_text)
            | Q(address__client__name__icontains=search_text)
            | Q(address__address__icontains=search_text)
            | Q(address__client__intern_code__icontains=search_text)
        ).values_list('id', flat=True)
        request.session["search_intervention"] = list(interventions)
        request.session["search_intervention_text"] = search_text
        return HttpResponseRedirect(reverse_lazy("intervention:intervention-search"))


class SearchInterventionView(TemplateView):
    template_name = "list_intervention.html"

    def get_context_data(self, **kwargs):
        context = super(SearchInterventionView, self).get_context_data(**kwargs)
        page = int(self.request.GET.get("page", 1))
        search_text = str(self.request.session.get("search_intervention_text", ""))
        context["title"] = "Búsqueda - " + search_text
        interventions_pk = self.request.session.get("search_intervention", list())
        interventions = Intervention.objects.filter(pk__in=interventions_pk).order_by(
            "-date"
        )
        elements_per_page = settings.DEFAULT_INTERVENTION_PAGINATOR
        if not self.request.user_agent.is_pc:
            elements_per_page = settings.DEFAULT_NUM_PAGINATOR
        paginator = Paginator(interventions, elements_per_page)
        context["interventions"] = get_page_from_paginator(paginator, page)
        return context


class ListModificationView(TemplateView):
    template_name = "list_modifications.html"

    def get_context_data(self, **kwargs):
        context = super(ListModificationView, self).get_context_data(**kwargs)
        page = int(self.request.GET.get("page", 1))
        modifications = InterventionModification.objects.all().order_by("-date")
        paginator = Paginator(modifications, settings.DEFAULT_MODIFICATIONS_PAGINATOR)
        context["modifications"] = get_page_from_paginator(paginator, page)
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
        m = int(request.GET.get("month", 0))
        y = int(request.GET.get("year", 0))

        if m > 0 and y > 0:
            d = generate_data_intervention_input(month=m, year=y)
        else:
            d = generate_data_intervention_input()

        return JsonResponse(data=d, safe=False)


class MorrisYearVs(MorrisView):
    def get(self, request, *args, **kwargs):
        return JsonResponse(data=generate_data_year_vs(), safe=False)


class PrintInterventionView(DetailView):
    template_name = "print_intervention.html"
    context_object_name = "intervention"
    model = Intervention


class PrintListInterventionView(ListInterventionView):
    template_name = "print_list_intervention.html"


class OwnListInterventionView(TemplateView):
    template_name = "list_intervention.html"

    def get_context_data(self, **kwargs):
        context = super(OwnListInterventionView, self).get_context_data(**kwargs)
        page = int(self.request.GET.get("page", 1))
        context["page"] = page
        context["title"] = "Mis averías asignadas"
        interventions = Intervention.objects.filter(
            status=settings.ASSIGNED_STATUS, assigned=self.request.user
        ).order_by("-date")
        elements_per_page = settings.DEFAULT_INTERVENTION_PAGINATOR
        if not self.request.user_agent.is_pc:
            elements_per_page = settings.DEFAULT_NUM_PAGINATOR
        paginator = Paginator(interventions, elements_per_page)
        context["interventions"] = get_page_from_paginator(paginator, page)

        return context


class ToggleStarredInterventionView(View):
    def get(self, request, *args, **kwargs):
        intervention = Intervention.objects.get(pk=self.kwargs["pk"])
        intervention.starred = not intervention.starred
        intervention.save()
        messages.success(self.request.user, "Cambio realizado correctamente")
        return HttpResponseRedirect(
            reverse_lazy(
                "intervention:intervention-view", kwargs={"pk": self.kwargs["pk"]}
            )
        )


class AddStatusJobView(View):
    def post(self, request, *args, **kwargs):
        status_id = int(request.POST.get("sub_status", 0))
        if status_id != 0:
            try:
                log = InterventionLogSub(
                    intervention_id=self.kwargs["pk"],
                    created_by=self.request.user,
                    sub_status_id=status_id,
                )
                log.save()
                messages.success(
                    self.request.user, "Notificación guardada correctamente"
                )
            except:
                messages.warning(
                    self.request.user, "No se han podido guardar los datos"
                )
        else:
            messages.warning(self.request.user, "No se han podido guardar los datos")
        return HttpResponseRedirect(
            reverse_lazy(
                "intervention:intervention-view", kwargs={"pk": self.kwargs["pk"]}
            )
        )


class ReportInterventionView(TemplateView):
    template_name = "report_intervention.html"

    def get_context_data(self, **kwargs):
        context = super(ReportInterventionView, self).get_context_data(**kwargs)
        context["statuses"] = InterventionStatus.objects.all()
        context["zones"] = Zone.objects.all()
        context["workers"] = User.objects.all()
        return context

    def post(self, request, *args, **kwargs):
        return generate_report(request)


class MapInterventionView(TemplateView):
    template_name = "map_assigned.html"

    def get_worker_id(self):
        return None

    def get_interventions(self):
        inter = Intervention.objects.filter(status_id=2)
        if self.get_worker_id():
            inter = inter.filter(assigned_id=self.get_worker_id())
        inter_result = []
        for i in inter:
            if i.address.get_geo():
                inter_result.append(i)
        return inter_result

    def get_context_data(self, **kwargs):
        context = super(MapInterventionView, self).get_context_data(**kwargs)
        context["gmaps_api"] = settings.GMAPS_API_KEY
        context["title"] = "todas las averías"
        context["interventions"] = self.get_interventions()
        context["users"] = User.objects.filter(is_active=True)
        return context


class MapAssignedInterventionView(MapInterventionView):
    def get_worker_id(self):
        return int(self.kwargs["pk"])

    def get_context_data(self, **kwargs):
        context = super(MapAssignedInterventionView, self).get_context_data(**kwargs)
        worker = User.objects.get(pk=self.get_worker_id())
        context["title"] = worker.get_full_name()
        return context


class ForbiddenInterventionView(TemplateView):
    template_name = "forbidden_intervention.html"


class LinkToInterventionView(View):
    def link_intervention(self, regex_text, text, type, trim=False):
        import re

        data = re.compile(regex_text).match(text)
        if data is not None:
            idstr = data.group()
            id = re.sub("[^0-9]", "", idstr)
            if trim:
                id = id[2:]
            id = int(id)
            intervention = Intervention.objects.get(pk=self.kwargs["pk"])
            if type == RepairType.ATH:
                intervention.repairs_ath.add(id)
            elif type == RepairType.IDEGIS:
                intervention.repairs_idegis.add(id)
            elif type == RepairType.ZODIAC:
                intervention.repairs_zodiac.add(id)
            elif type == "budget":
                intervention.budgets.add(id)
            messages.success(self.request.user, "Vinculación correcta")
            return True
        else:
            return False

    def post(self, request, *args, **kwargs):
        text = request.POST.get("object", "")
        search_text = str(text).replace(" ", "")

        try:
            found = False

            found = found | self.link_intervention(
                IDEGIS_REGEX, search_text, RepairType.IDEGIS
            )

            if not found:
                found = found | self.link_intervention(
                    ATH_REGEX, search_text, RepairType.ATH
                )

            if not found:
                found = found | self.link_intervention(
                    ZODIAC_REGEX, search_text, RepairType.ZODIAC
                )

            if not found:
                found = found | self.link_intervention(
                    BUDGET_REGEX, search_text, "budget"
                )

            if not found:
                found = found | self.link_intervention(
                    BUDGET_REGEX_2ND_FORMAT, search_text, "budget", trim=True
                )

            if not found:
                found = found | self.link_intervention(
                    BUDGET_REGEX_3RD_FORMAT, search_text, "budget", trim=True
                )

            if not found:
                messages.warning(
                    self.request.user,
                    "No se ha podido vincular la avería debido a un error, "
                    "puede ser que el número sea incorrecto",
                )

        except:
            messages.warning(
                self.request.user,
                "No se ha podido vincular la avería V%d debido a un error, "
                "puede ser que el número sea incorrecto." % int(kwargs["pk"]),
            )

        return HttpResponseRedirect(
            reverse_lazy("intervention:intervention-view", kwargs={"pk": kwargs["pk"]})
        )


class InterventionFilesView(View):
    def get(self, request, *args, **kwargs):
        intervention = Intervention.objects.get(pk=kwargs['pk'])
        return get_items_in_json_response(intervention, kwargs['file_type'], request.user,
                                          'intervention:intervention-file-download', kwargs,
                                          'intervention:intervention-file')

    def post(self, request, *args, **kwargs):
        intervention = Intervention.objects.get(pk=kwargs['pk'])
        return store_file_metadata_from_post(request.POST, intervention, kwargs['file_type'], request.user)


class InterventionFileView(View):
    def delete(self, request, *args, **kwargs):
        intervention = Intervention.objects.get(pk=kwargs['pk'])
        return delete_file_metadata(kwargs['file_id'], intervention, kwargs['file_type'], request.user)

    def put(self, request, *args, **kwargs):
        intervention = Intervention.objects.get(pk=kwargs['pk'])
        visible = QueryDict(request.body).get('visible', 'false') == 'true'
        return update_file_metadata(kwargs['file_id'], intervention, kwargs['file_type'], request.user, visible)

    def get(self, request, *args, **kwargs):
        intervention = Intervention.objects.get(pk=kwargs['pk'])
        return get_file_metadata(kwargs['file_id'], intervention, kwargs['file_type'], request.user,
                                 'intervention:intervention-file-download', kwargs, 'intervention:intervention-file')


class InterventionFileDownloadView(View):
    def get(self, request, *args, **kwargs):
        intervention = Intervention.objects.get(pk=kwargs['pk'])
        return get_file_download_url(kwargs['file_id'], intervention, kwargs['file_type'], request.user)
