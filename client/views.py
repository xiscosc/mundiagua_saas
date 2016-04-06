from django.core.urlresolvers import reverse_lazy
from django.views.generic import CreateView, DetailView, UpdateView

from client.models import Client, Address, Phone


class CreateClientView(CreateView):
    model = Client
    fields = "__all__"
    template_name = 'new_client.html'

    def get_context_data(self, **kwargs):
        context = super(CreateClientView, self).get_context_data(**kwargs)
        context['title'] = "Nuevo cliente"
        return context

    def get_success_url(self):
        return reverse_lazy('client-address-new', kwargs={'id': self.object.pk})


class CreateAddressView(CreateView):
    model = Address
    fields = ["alias", "address"]
    template_name = "new_address.html"

    def get_context_data(self, **kwargs):
        context = super(CreateAddressView, self).get_context_data(**kwargs)
        context['client'] = Client.objects.get(id=self.kwargs['id'])
        addresses = Address.objects.filter(client=self.kwargs['id'])
        context['skip'] = (len(addresses) > 0)
        return context

    def form_valid(self, form):
        address = form.save(commit=False)
        address.client = Client.objects.get(id=self.kwargs['id'])
        return super(CreateAddressView, self).form_valid(form)

    def get_success_url(self):
        if self.request.resolver_match.url_name == "client-address-new":
            return reverse_lazy('client-phone-new', kwargs={'id': self.object.client.pk})
        else:
            return reverse_lazy('client-client', kwargs={'pk': self.object.client.pk})


class CreatePhoneAddress(CreateView):
    model = Phone
    fields = ["alias", "phone"]
    template_name = "new_phone.html"
    success_url = reverse_lazy('intervention-home')

    def get_context_data(self, **kwargs):
        context = super(CreatePhoneAddress, self).get_context_data(**kwargs)
        context['client'] = Client.objects.get(id=self.kwargs['id'])
        return context

    def form_valid(self, form):
        phone = form.save(commit=False)
        phone.client = Client.objects.get(id=self.kwargs['id'])
        return super(CreatePhoneAddress, self).form_valid(form)

    def get_success_url(self):
        return reverse_lazy('client-client', kwargs={'pk': self.object.client.pk})


class ClientView(DetailView):
    context_object_name = "client"
    model = Client
    template_name = "detail_client.html"

    def get_context_data(self, **kwargs):
        context = super(ClientView, self).get_context_data(**kwargs)
        context['addresses'] = Address.objects.filter(client=self.object)
        context['phones'] = Phone.objects.filter(client=self.object)
        return context


class EditClientView(UpdateView):
    model = Client
    template_name = 'new_client.html'
    fields = '__all__'

    def get_context_data(self, **kwargs):
        context = super(EditClientView, self).get_context_data(**kwargs)
        context['title'] = "Editar cliente"
        return context

    def get_success_url(self):
        return reverse_lazy('client-client', kwargs={'pk': self.object.pk})


class EditPhoneView(UpdateView):
    model = Phone
    template_name = "new_phone.html"
    fields = ["alias", "phone"]

    def get_success_url(self):
        return reverse_lazy('client-client', kwargs={'pk': self.object.client.pk})

    def get_context_data(self, **kwargs):
        context = super(EditPhoneView, self).get_context_data(**kwargs)
        context['client'] = self.object.client
        return context


class EditAddressView(UpdateView):
    model = Address
    template_name = "new_address.html"
    fields = ["alias", "address"]

    def get_success_url(self):
        return reverse_lazy('client-client', kwargs={'pk': self.object.client.pk})

    def get_context_data(self, **kwargs):
        context = super(EditAddressView, self).get_context_data(**kwargs)
        context['addresses'] = Address.objects.filter(client=self.object.client).exclude(pk=self.object.pk)
        context['can_delete'] = (len(context['addresses']) > 0)
        return context
