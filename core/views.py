from django.core.paginator import Paginator
from django.core.urlresolvers import reverse_lazy
from django.http import HttpResponseRedirect, JsonResponse, Http404
from django.shortcuts import render_to_response

# Create your views here.
from django.template import RequestContext
from django.views.generic import TemplateView
from django.views.generic.base import View
from django.views.generic.edit import CreateView

from client.models import Client, Address
from core.models import User, Message


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


class CreateBaseView(CreateView):
    template_name = "new_base.html"

    def get_form(self, form_class=None):
        form = super(CreateBaseView, self).get_form(form_class=form_class)
        try:
            form.fields['address'].queryset = Address.objects.filter(client=self.kwargs['id'])
        except:
            pass
        return form

    def get_context_data(self, **kwargs):
        context = super(CreateBaseView, self).get_context_data(**kwargs)
        try:
            context['client'] = Client.objects.get(pk=self.kwargs['id'])
        except:
            pass
        return context

    def form_valid(self, form):
        obj = form.save(commit=False)
        obj.created_by = self.request.user
        return super(CreateBaseView, self).form_valid(form)


class IndexView(View):

    def dispatch(self, request, *args, **kwargs):

        if request.user.is_authenticated() and request.user.is_active:
            return HttpResponseRedirect(reverse_lazy('intervention:intervention-home'))
        else:
            return HttpResponseRedirect(reverse_lazy('login'))


class NewMessageView(CreateView):
    template_name = "new_message.html"
    model = Message
    fields = ['to_user', 'subject', 'body']
    success_url = reverse_lazy('message-sent')

    def get_form(self, form_class=None):
        form = super(NewMessageView, self).get_form(form_class=form_class)
        form.fields['to_user'].queryset = User.objects.all().exclude(pk=self.request.user.pk)
        return form

    def form_valid(self, form):
        obj = form.save(commit=False)
        obj.from_user = self.request.user
        return super(NewMessageView, self).form_valid(form)


class MessageListBaseView(TemplateView):
    template_name = "list_message.html"

    def get_data(self):
        pass

    def get_context_data(self, **kwargs):
        context = super(MessageListBaseView, self).get_context_data(**kwargs)
        page = int(self.request.GET.get('page', 1))
        messages = self.get_data()
        paginator = Paginator(messages, 10)
        context['messages_mundiagua'] = paginator.page(page)
        return context


class MessagesListView(MessageListBaseView):

    def get_data(self):
        return Message.objects.filter(to_user=self.request.user).order_by("-date")


class MessagesSentListView(MessageListBaseView):

    def get_data(self):
        return Message.objects.filter(from_user=self.request.user).order_by("-date")


class MessagesAjaxView(TemplateView):
    template_name = "ajax_messages.html"

    def get_context_data(self, **kwargs):
        context = super(MessagesAjaxView, self).get_context_data(**kwargs)
        context['messages_mundiagua'] = Message.objects.filter(to_user=self.request.user).order_by("-date")[:3]
        return context
