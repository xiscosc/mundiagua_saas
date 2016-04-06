from django.shortcuts import render, render_to_response

# Create your views here.
from django.template import RequestContext
from django.views.generic import TemplateView

from client.models import Client


class SearchClientBaseView(TemplateView):
    template_name = 'search_client.html'

    def post(self, request, *args, **kwargs):
        search = request.POST.getlist('search')[0]
        context = self.get_context_data()
        context['clients'] = Client.objects.filter(name__icontains=search)
        context['show_results'] = len(context['clients'])
        return render_to_response(self.template_name, context, context_instance=RequestContext(request))

    def get_context_data(self, **kwargs):
        context = super(SearchClientBaseView, self).get_context_data(**kwargs)
        context['show_results'] = -1
        return context