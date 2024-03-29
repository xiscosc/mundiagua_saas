from django.conf import settings
from django.core.paginator import Paginator
from django.urls import reverse_lazy
from django.db.models import Q
from django.forms.models import model_to_dict
from django.http import HttpResponseRedirect, HttpResponse, JsonResponse
from django.shortcuts import render
from django.views.generic import (
    CreateView,
    DetailView,
    UpdateView,
    DeleteView,
    View,
    TemplateView,
)
from client.models import Client, Address, Phone, SMS, Email
from core.utils import get_page_from_paginator
from core.views import PreSearchView
from engine.models import EngineRepair
from intervention.models import Intervention
from repair.models import AthRepair, IdegisRepair, ZodiacRepair, RepairType
from budget.models import BudgetStandard, BudgetRepair
from core.tasks import (
    send_mail_client,
    send_mail_client_with_pdf,
)
from async_messages import messages


class CreateClientView(CreateView):
    model = Client
    fields = ["name", "intern_code", "dni"]
    template_name = "new_client.html"

    def get_context_data(self, **kwargs):
        context = super(CreateClientView, self).get_context_data(**kwargs)
        context["title"] = "Nuevo cliente"
        return context

    def get_success_url(self):
        return reverse_lazy("client:client-address-new", kwargs={"id": self.object.pk})


class CreateAddressView(CreateView):
    model = Address
    fields = ["alias", "address"]
    template_name = "new_address.html"

    def get_context_data(self, **kwargs):
        context = super(CreateAddressView, self).get_context_data(**kwargs)
        context["client"] = Client.objects.get(id=self.kwargs["id"])
        return context

    def form_valid(self, form):
        address = form.save(commit=False)
        address.client = Client.objects.get(id=self.kwargs["id"])
        return super(CreateAddressView, self).form_valid(form)

    def get_success_url(self):
        other = int(self.request.POST.getlist("other")[0])
        if other == 0:
            if self.request.resolver_match.url_name == "client-address-new":
                return reverse_lazy(
                    "client:client-phone-new", kwargs={"id": self.object.client.pk}
                )
            else:
                return reverse_lazy(
                    "client:client-view", kwargs={"pk": self.object.client.pk}
                )
        else:
            return reverse_lazy(
                "client:client-address-new", kwargs={"id": self.object.client.pk}
            )


class CreatePhoneView(CreateView):
    model = Phone
    fields = ["alias", "international_code", "phone"]
    template_name = "new_phone.html"

    def get_context_data(self, **kwargs):
        context = super(CreatePhoneView, self).get_context_data(**kwargs)
        context["client"] = Client.objects.get(id=self.kwargs["id"])
        return context

    def form_valid(self, form):
        phone = form.save(commit=False)
        phone.client = Client.objects.get(id=self.kwargs["id"])
        return super(CreatePhoneView, self).form_valid(form)

    def get_success_url(self):
        other = int(self.request.POST.getlist("other")[0])
        if other == 0:
            if self.request.resolver_match.url_name == "client-phone-new":
                return reverse_lazy(
                    "client:client-email-new", kwargs={"id": self.object.client.pk}
                )
            else:
                return reverse_lazy(
                    "client:client-view", kwargs={"pk": self.object.client.pk}
                )
        else:
            return reverse_lazy(
                "client:client-phone-new", kwargs={"id": self.object.client.pk}
            )


class CreateEmailView(CreateView):
    model = Email
    fields = ["alias", "email"]
    template_name = "new_email.html"

    def get_context_data(self, **kwargs):
        context = super(CreateEmailView, self).get_context_data(**kwargs)
        context["client"] = Client.objects.get(id=self.kwargs["id"])
        return context

    def form_valid(self, form):
        email = form.save(commit=False)
        email.client = Client.objects.get(id=self.kwargs["id"])
        return super(CreateEmailView, self).form_valid(form)

    def get_success_url(self):
        other = int(self.request.POST.getlist("other")[0])
        if other == 0:
            return reverse_lazy(
                "client:client-view", kwargs={"pk": self.object.client.pk}
            )
        else:
            return reverse_lazy(
                "client:client-email-new", kwargs={"id": self.object.client.pk}
            )


class ClientView(DetailView):
    context_object_name = "client"
    model = Client
    template_name = "detail_client.html"

    def get_context_data(self, **kwargs):
        context = super(ClientView, self).get_context_data(**kwargs)
        repairs_ath = AthRepair.objects.filter(
            address__client=context["object"]
        ).count()
        repairs_idegis = IdegisRepair.objects.filter(
            address__client=context["object"]
        ).count()
        repairs_zodiac = ZodiacRepair.objects.filter(
            address__client=context["object"]
        ).count()
        context["interventions"] = Intervention.objects.filter(
            address__client=context["object"]
        ).count()
        context["repairs"] = repairs_ath + repairs_idegis + repairs_zodiac
        context["engines"] = EngineRepair.objects.filter(
            address__client=context["object"]
        ).count()
        context["budgets"] = BudgetStandard.objects.filter(
            address__client=context["object"]
        ).count()
        return context


class InterventionsFromCustomerView(View):
    def get(self, request, *args, **kwargs):
        customer = Client.objects.get(pk=kwargs["pk"])
        pk_list = list(
            Intervention.objects.filter(address__client=customer).order_by("-date").values_list('id', flat=True))
        request.session["search_intervention"] = pk_list
        request.session["search_intervention_text"] = "Averías de " + str(customer)
        return HttpResponseRedirect(reverse_lazy("intervention:intervention-search"))


class BudgetsFromCustomerView(View):
    def get(self, request, *args, **kwargs):
        customer = Client.objects.get(pk=kwargs["pk"])
        pk_list = list(
            BudgetStandard.objects.filter(address__client=customer).order_by("-date").values_list('id', flat=True))
        request.session["search_budgets"] = pk_list
        request.session["search_budgets_text"] = "Presupuestos de " + str(customer)
        request.session["search_budgets_lines_enabled"] = False
        return HttpResponseRedirect(reverse_lazy("budget:budget-search"))


class EngineRepairsFromCustomerView(View):
    def get(self, request, *args, **kwargs):
        customer = Client.objects.get(pk=kwargs["pk"])
        pk_list = list(
            EngineRepair.objects.filter(address__client=customer).order_by("-date").values_list('id', flat=True))
        request.session["search_repairs_engine"] = pk_list
        request.session[
            "search_repairs_engine_text"
        ] = "Reparaciones de motor de " + str(customer)
        return HttpResponseRedirect(reverse_lazy("engine:engine-search"))


class RepairsFromCustomerView(View):
    def get(self, request, *args, **kwargs):
        customer = Client.objects.get(pk=kwargs["pk"])
        request.session["search_repair_ath"] = list(
            AthRepair.objects.filter(address__client=customer)
                .order_by("-date")
                .values_list("id", flat=True)
        )
        request.session["search_repair_idegis"] = list(
            IdegisRepair.objects.filter(address__client=customer)
                .order_by("-date")
                .values_list("id", flat=True)
        )
        request.session["search_repair_zodiac"] = list(
            ZodiacRepair.objects.filter(address__client=customer)
                .order_by("-date")
                .values_list("id", flat=True)
        )
        request.session["search_repair_text"] = "Reparaciones de " + str(customer)
        return HttpResponseRedirect(
            reverse_lazy(
                "repair:repair-search",
                kwargs={"type": RepairType.ALL.value, "starred": 0},
            )
        )


class EditClientView(UpdateView):
    model = Client
    template_name = "new_client.html"
    fields = "__all__"

    def get_context_data(self, **kwargs):
        context = super(EditClientView, self).get_context_data(**kwargs)
        context["title"] = "Editar cliente"
        return context

    def get_success_url(self):
        return reverse_lazy("client:client-view", kwargs={"pk": self.object.pk})


class EditPhoneView(UpdateView):
    model = Phone
    template_name = "new_phone.html"
    fields = ["alias", "international_code", "phone"]

    def get_success_url(self):
        return reverse_lazy("client:client-view", kwargs={"pk": self.object.client.pk})

    def get_context_data(self, **kwargs):
        context = super(EditPhoneView, self).get_context_data(**kwargs)
        context["client"] = self.object.client
        return context


class EditEmailView(UpdateView):
    model = Email
    template_name = "new_email.html"
    fields = ["alias", "email"]

    def get_success_url(self):
        return reverse_lazy("client:client-view", kwargs={"pk": self.object.client.pk})

    def get_context_data(self, **kwargs):
        context = super(EditEmailView, self).get_context_data(**kwargs)
        context["client"] = self.object.client
        return context


class EditAddressView(UpdateView):
    model = Address
    template_name = "new_address.html"
    fields = ["alias", "address", "latitude", "longitude"]

    def get_success_url(self):
        return reverse_lazy("client:client-view", kwargs={"pk": self.object.client.pk})

    def get_context_data(self, **kwargs):
        context = super(EditAddressView, self).get_context_data(**kwargs)
        context["client"] = self.object.client
        return context


class DeletePhoneView(DeleteView):
    model = Phone
    context_object_name = "phone"
    template_name = "delete_phone.html"

    def get_success_url(self):
        return reverse_lazy("client:client-view", kwargs={"pk": self.object.client.pk})


class DeleteEmailView(DeleteView):
    model = Email
    context_object_name = "email"
    template_name = "delete_email.html"

    def get_success_url(self):
        return reverse_lazy("client:client-view", kwargs={"pk": self.object.client.pk})


class DeleteAddresView(DeleteView):
    model = Address
    context_object_name = "address"
    template_name = "delete_address.html"

    def get_context_data(self, **kwargs):
        context = super(DeleteAddresView, self).get_context_data(**kwargs)
        context["addresses"] = Address.objects.filter(
            client=self.object.client
        ).exclude(pk=self.object.pk)
        context["can_delete"] = len(context["addresses"]) > 0
        return context

    def get_success_url(self):
        return reverse_lazy("client:client-view", kwargs={"pk": self.object.client.pk})

    def delete(self, request, *args, **kwargs):
        new_address_id = int(self.request.POST.getlist("new_address")[0])
        Intervention.objects.filter(address=int(self.kwargs["pk"])).update(
            address_id=new_address_id
        )
        AthRepair.objects.filter(address=int(self.kwargs["pk"])).update(
            address_id=new_address_id
        )
        IdegisRepair.objects.filter(address=int(self.kwargs["pk"])).update(
            address_id=new_address_id
        )
        BudgetStandard.objects.filter(address=int(self.kwargs["pk"])).update(
            address_id=new_address_id
        )
        BudgetRepair.objects.filter(address=int(self.kwargs["pk"])).update(
            address_id=new_address_id
        )
        EngineRepair.objects.filter(address=int(self.kwargs["pk"])).update(
            address_id=new_address_id
        )

        return super(DeleteAddresView, self).delete(request, *args, **kwargs)

    def change_address(self, set_data, new_address_id):
        for i in set_data:
            i.address_id = new_address_id
            i.save()


class SendSMSView(View):
    def post(self, request, *args, **kwargs):
        params = request.POST.copy()
        sms = SMS(
            sender=request.user,
            body=params.getlist("sms_body")[0],
            phone_id=int(params.getlist("phone_pk")[0]),
        )
        sms.save()
        sms.send()
        try:
            model = params.getlist("from_model")[0]
            id_model = params.getlist("from_model_id")[0]
            if model == "intervention":
                obj = Intervention.objects.get(pk=id_model)
            elif model == "repair-ath":
                obj = AthRepair.objects.get(pk=id_model)
            elif model == "repair-idegis":
                obj = IdegisRepair.objects.get(pk=id_model)
            elif model == "repair-engine":
                obj = EngineRepair.objects.get(pk=id_model)
            obj.sms.add(sms)
        except:
            pass

        return HttpResponseRedirect(request.META.get("HTTP_REFERER", "/"))


class SendEmailView(View):
    def post(self, request, *args, **kwargs):
        body = request.POST.get("email_body", "")
        subject = request.POST.get("email_subject", "")
        email_pk = request.POST.get("email_field", "")
        attachment_id = request.POST.get("attachment_id", "")

        if email_pk == "":
            return HttpResponseRedirect(request.META.get("HTTP_REFERER", "/"))

        if attachment_id == "":
            send_mail_client(email_pk, subject, body, request.user.pk)
        else:
            send_mail_client_with_pdf(
                email_pk, subject, body, request.user.pk, attachment_id
            )

        return HttpResponseRedirect(request.META.get("HTTP_REFERER", "/"))


class AllClientsView(TemplateView):
    template_name = "list_client.html"

    def get_context_data(self, **kwargs):
        context = super(AllClientsView, self).get_context_data(**kwargs)
        page = int(self.request.GET.get("page", 1))
        clients = Client.objects.all().order_by("pk")
        context["title"] = "Todos los clientes"
        paginator = Paginator(clients, settings.DEFAULT_CLIENTS_PAGINATOR)
        context["clients"] = get_page_from_paginator(paginator, page)
        return context


class PreSearchClientView(PreSearchView):
    def set_data_and_response(self, request):
        search_text = self.search_text
        clients = Client.objects.filter(
            Q(name__icontains=search_text) | Q(intern_code__icontains=search_text)
        )
        addresses = Address.objects.filter(address__icontains=search_text)
        phones = Phone.objects.filter(phone__icontains=search_text)
        pk_list = []
        for i in clients:
            pk_list.append(i.pk)
        for a in addresses:
            pk_list.append(a.client_id)
        for p in phones:
            pk_list.append(p.client_id)
        request.session["search_clients"] = list(set(pk_list))
        request.session["search_clients_text"] = search_text
        return HttpResponseRedirect(reverse_lazy("client:client-search"))


class SearchClientView(TemplateView):
    template_name = "list_client.html"

    def get_context_data(self, **kwargs):
        context = super(SearchClientView, self).get_context_data(**kwargs)
        page = int(self.request.GET.get("page", 1))
        search_text = str(self.request.session.get("search_clients_text", ""))
        context["title"] = "Búsqueda - " + search_text
        clients_pk = self.request.session.get("search_clients", list())
        clients = Client.objects.filter(pk__in=clients_pk)
        paginator = Paginator(clients, settings.DEFAULT_CLIENTS_PAGINATOR)
        context["clients"] = get_page_from_paginator(paginator, page)
        return context


class AddressGeoUpdateView(View):
    def post(self, request, *args, **kwargs):
        params = request.POST.copy()
        address = Address.objects.get(pk=kwargs["pk"])
        address.latitude = params["lat"]
        address.longitude = params["lon"]
        address.save()
        return HttpResponse("OK")


class SearchClientToReplaceView(TemplateView):
    template_name = "merge_client.html"

    def post(self, request, *args, **kwargs):
        search = request.POST.getlist("search")[0]
        context = self.get_context_data()
        context["clients"] = Client.objects.filter(name__icontains=search)
        context["show_results"] = len(context["clients"])
        return render(request, self.template_name, context)

    def get_context_data(self, **kwargs):
        context = super(SearchClientToReplaceView, self).get_context_data(**kwargs)
        context["show_results"] = -1
        context["title"] = "Fusión de clientes"
        context["subtitle"] = "Paso 1: Seleccionar cliente a borrar"
        context["new_url"] = "client:client-merge-step2"
        context["btn_text"] = "Seleccionar como cliente a borrar"
        context["btn_class"] = "btn-danger"
        return context


class SearchClientToMergeView(TemplateView):
    template_name = "merge_client.html"

    def post(self, request, *args, **kwargs):
        search = request.POST.getlist("search")[0]
        context = self.get_context_data()
        context["clients"] = Client.objects.filter(name__icontains=search)
        context["show_results"] = len(context["clients"])
        client = Client.objects.get(pk=kwargs["pk"])
        context["subtitle"] = (
                "Paso 2: Seleccionar cliente a fusionar con %s" % client.name
        )
        context["client_obj"] = client
        return render(request, self.template_name, context)

    def get_context_data(self, **kwargs):
        context = super(SearchClientToMergeView, self).get_context_data(**kwargs)
        try:
            client = Client.objects.get(pk=kwargs["pk"])
            context["subtitle"] = (
                    "Paso 2: Seleccionar cliente a fusionar con %s" % client.name
            )
        except:
            pass
        context["show_results"] = -1
        context["title"] = "Fusión de clientes"
        context["new_url"] = "client:client-merge-step3"
        context["btn_text"] = "Seleccionar como cliente a fusionar"
        context["btn_class"] = "btn-success"
        return context


class ClientMergeView(TemplateView):
    template_name = "merge_client_confirmation.html"

    def post(self, request, *args, **kwargs):
        client_old = Client.objects.get(pk=kwargs["pk1"])
        client_new = Client.objects.get(pk=kwargs["pk2"])

        Address.objects.filter(client=client_old).update(client=client_new)
        Phone.objects.filter(client=client_old).update(client=client_new)
        Email.objects.filter(client=client_old).update(client=client_new)

        client_old.delete()

        messages.success(request.user, "Clientes fusionados correctamente")
        return HttpResponseRedirect(
            reverse_lazy("client:client-view", kwargs={"pk": client_new.pk})
        )

    def get_context_data(self, **kwargs):
        context = super(ClientMergeView, self).get_context_data(**kwargs)
        context["client_old"] = Client.objects.get(pk=kwargs["pk1"])
        context["client_new"] = Client.objects.get(pk=kwargs["pk2"])
        context["title"] = "Fusión de clientes - Confirmación"
        return context
