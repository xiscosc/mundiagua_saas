from django.core.urlresolvers import reverse_lazy
from django.views.generic import CreateView

from client.models import Client, Address


class CreateClientView(CreateView):
    model = Client
    fields = "__all__"
    template_name = 'new_client.html'

    def get_success_url(self):
        return reverse_lazy('client-address-new', kwargs={'id': self.object.pk})


class CreateAddressView(CreateView):
    model = Address
    fields = ["alias", "address"]
    template_name = "new_address.html"
    success_url = reverse_lazy('intervention-home')

    def get_context_data(self, **kwargs):
        context = super(CreateAddressView, self).get_context_data(**kwargs)
        context['client'] = Client.objects.get(id=self.kwargs['id'])
        return context
