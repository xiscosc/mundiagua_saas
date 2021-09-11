from django.core.paginator import Paginator
from django.urls import reverse_lazy
from django.http import HttpResponseRedirect, Http404, JsonResponse
from django.shortcuts import render
from django.conf import settings
from django.views.generic import TemplateView
from django.views.generic.base import View
from django.views.generic.edit import CreateView, UpdateView
from django.contrib.auth import logout
from client.models import Client, Address
from core.forms import SystemVariableRichForm, SystemVariablePlainForm
from core.models import User, Message, SystemVariable
from core.utils import get_return_from_id, has_to_change_password, get_page_from_paginator, get_sms_api
from core.tasks import notify_sms_received
from engine.models import EngineRepair, EngineStatus
from repair.models import RepairStatus
from urllib.parse import urlencode


class SearchClientBaseView(TemplateView):
    template_name = 'search_client.html'

    def post(self, request, *args, **kwargs):
        search = request.POST.getlist('search')[0]
        context = self.get_context_data()
        context['clients'] = Client.objects.filter(name__icontains=search)
        context['show_results'] = len(context['clients'])
        return render(request, self.template_name, context)

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

        engine_pk = int(self.request.GET.get('engine', 0))
        if engine_pk is not 0:
            self.request.session['engine_budget'] = engine_pk
            context['engine'] = EngineRepair.objects.get(pk=engine_pk)
        else:
            self.request.session['engine_budget'] = 0

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
        if request.user.is_authenticated and request.user.is_active:
            if request.user.is_officer:
                response = 'intervention:intervention-home'
            else:
                response = 'intervention:intervention-list-own'
        else:
            return HttpResponseRedirect(settings.LOGIN_URL)
        return HttpResponseRedirect(reverse_lazy(response))


class NewMessageView(CreateView):
    template_name = "new_message.html"
    model = Message
    fields = ['to_user', 'subject', 'body']
    success_url = reverse_lazy('core:message-sent')

    def get_form(self, form_class=None):
        form = super(NewMessageView, self).get_form(form_class=form_class)
        users = User.objects.filter(is_active=True).exclude(pk=self.request.user.pk)
        form.fields['to_user'].choices = [(u.pk, u.get_full_name()) for u in users]
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
        context['messages_mundiagua'] = get_page_from_paginator(paginator, page)
        return context


class MessagesListView(MessageListBaseView):

    def get_data(self):
        return Message.objects.filter(to_user=self.request.user).order_by("-date")

    def get_context_data(self, **kwargs):
        context = super(MessagesListView, self).get_context_data(**kwargs)
        context['inbox'] = True
        if self.request.user.has_notification > 0:
            self.request.user.has_notification = 0
            self.request.user.save()
        return context


class MessagesSentListView(MessageListBaseView):

    def get_data(self):
        return Message.objects.filter(from_user=self.request.user).order_by("-date")


class MessagesAjaxView(TemplateView):
    template_name = "ajax_messages.html"

    def get_context_data(self, **kwargs):
        context = super(MessagesAjaxView, self).get_context_data(**kwargs)
        context['messages_mundiagua'] = Message.objects.filter(to_user=self.request.user).order_by("-date")[:3]
        context['has_notification'] = self.request.user.has_notification
        if context['has_notification'] == 1:
            self.request.user.has_notification = 2
            self.request.user.save()
        return context


class GetAllSmsView(View):
    def dispatch(self, request, *args, **kwargs):
        if not request.is_ajax():
            raise Http404("This is an ajax view, friend.")
        return super(GetAllSmsView, self).dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        limit = request.GET.get('limit', 0)
        offset = request.GET.get('offset', 0)
        response_code, response = get_sms_api('/sms/all', limit, offset)
        if response_code == 200:
            return JsonResponse(data=response, safe=False)
        else:
            raise Http404(response)


class GetSmsBySenderView(View):
    def dispatch(self, request, *args, **kwargs):
        if not request.is_ajax():
            raise Http404("This is an ajax view, friend.")
        return super(GetSmsBySenderView, self).dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        limit = request.GET.get('limit', 0)
        offset = request.GET.get('offset', 0)
        sender = kwargs['sender']
        response_code, response = get_sms_api('/sms/sender/' + sender, limit, offset)
        if response_code == 200:
            return JsonResponse(data=response, safe=False)
        else:
            raise Http404(response)


class GetSmsView(View):
    def dispatch(self, request, *args, **kwargs):
        if not request.is_ajax():
            raise Http404("This is an ajax view, friend.")
        return super(GetSmsView, self).dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        id = kwargs['id']
        response_code, response = get_sms_api('/sms/' + id)
        if response_code == 200:
            return JsonResponse(data=response, safe=False)
        else:
            raise Http404(response)


class NotifySmsView(View):
    def get(self, request, *args, **kwargs):
        notify_sms_received()
        return JsonResponse(data="OK", safe=False)


class SMSListView(TemplateView):
    template_name = 'sms_list.html'

    def get_context_data(self, **kwargs):
        context = super(SMSListView, self).get_context_data(**kwargs)
        context['gsm_phone'] = settings.SMS_SERVICE_PHONE
        return context


class SMSSenderListView(TemplateView):
    template_name = 'sms_list.html'

    def get_context_data(self, **kwargs):
        context = super(SMSSenderListView, self).get_context_data(**kwargs)
        context['phone'] = kwargs['sender']
        context['gsm_phone'] = settings.SMS_SERVICE_PHONE
        return context


class PreSearchView(View):

    search_text = None

    def get(self, request, *args, **kwargs):
        return HttpResponseRedirect(reverse_lazy('home'))

    def set_data_and_response(self, request):
        return None

    def post(self, request, *args, **kwargs):
        params = request.POST.copy()
        search_text = params.getlist('search_text')[0]
        self.search_text = search_text
        regex_data = get_return_from_id(self.search_text)
        if regex_data['found']:
            return HttpResponseRedirect(regex_data['url'])
        else:
            return self.set_data_and_response(request=request)


class ChangeLogView(TemplateView):
    template_name = "changelog.html"

    def get_context_data(self, **kwargs):
        context = super(ChangeLogView, self).get_context_data(**kwargs)
        import django, boto3, sendgrid, sys, celery, memcache, psycopg2
        from django.core.cache import cache
        context['intranet_version'] = settings.APP_COMPLETE_VERSION
        context['django_version'] = django.__version__
        context['amazon_version'] = boto3.__version__
        context['sendgrid_version'] = sendgrid.__version__
        context['celery_version'] = celery.__version__
        context['python_version'] = sys.version
        context['memcache_version'] = memcache.__version__
        context['postgre_version_c'] = psycopg2.__version__
        context['postgre_version'] = psycopg2.__libpq_version__
        context['gsm_time'] = cache.get(settings.GSM_WATCH_TIME_CACHE_KEY)
        context['gsm_phone'] = settings.SMS_SERVICE_PHONE
        return context


class SystemVariableView(TemplateView):
    template_name = "system_variables.html"

    def get_context_data(self, **kwargs):
        context = super(SystemVariableView, self).get_context_data(**kwargs)
        context['variables'] = SystemVariable.objects.all().order_by('type')
        return context


class RepairStatusSystemView(TemplateView):
    template_name = "system_repair_status.html"

    def get_context_data(self, **kwargs):
        context = super(RepairStatusSystemView, self).get_context_data(**kwargs)
        context['variables'] = RepairStatus.objects.all().order_by('percentage')
        context['title'] = 'Estados reparación Idegis & ATH'
        context['newurl'] = 'core:repair-status-new'
        context['editurl'] = 'core:repair-status-edit'
        return context


class EngineRepairStatusSystemView(TemplateView):
    template_name = "system_repair_status.html"

    def get_context_data(self, **kwargs):
        context = super(EngineRepairStatusSystemView, self).get_context_data(**kwargs)
        context['variables'] = EngineStatus.objects.all().order_by('percentage')
        context['title'] = 'Estados reparación de motores'
        context['newurl'] = 'core:engine-repair-status-new'
        context['editurl'] = 'core:engine-repair-status-edit'
        return context


class SystemVariableUpdateView(UpdateView):
    model = SystemVariable
    template_name = 'system_variable_edit.html'
    success_url = reverse_lazy('core:variable')

    def get_form_class(self):
        if self.object.rich_text:
            return SystemVariableRichForm
        else:
            return SystemVariablePlainForm


class SystemRepairStatusUpdateView(UpdateView):
    model = RepairStatus
    template_name = 'system_repair_status_edit.html'
    success_url = reverse_lazy('core:repair-status')
    fields = '__all__'


class SystemRepairStatusCreateView(CreateView):
    model = RepairStatus
    template_name = 'system_repair_status_edit.html'
    success_url = reverse_lazy('core:repair-status')
    fields = '__all__'


class SystemEngineRepairStatusUpdateView(UpdateView):
    model = EngineStatus
    template_name = 'system_repair_status_edit.html'
    success_url = reverse_lazy('core:engine-repair-status')
    fields = '__all__'


class SystemEngineRepairStatusCreateView(CreateView):
    model = EngineStatus
    template_name = 'system_repair_status_edit.html'
    success_url = reverse_lazy('core:engine-repair-status')
    fields = '__all__'


class PrivacyView(TemplateView):
    template_name = 'privacy.html'


class UserView(TemplateView):
    template_name = 'user.html'

    def get_context_data(self, **kwargs):
        context = super(UserView, self).get_context_data(**kwargs)
        context['telegran_name'] = settings.TELEGRAM_NAME
        return context


class LoginErrorView(TemplateView):
    template_name = 'login_error.html'


class LoginErrorAuthView(TemplateView):
    template_name = 'login_error_auth.html'


class LoginView(TemplateView):
    template_name = 'login_auth0.html'


class RedirectLoginView(View):
    def get(self, request, *args, **kwargs):
        return HttpResponseRedirect(reverse_lazy('login'))


class LogoutView(View):
    def get(self, request, *args, **kwargs):
        logout(request)
        return_to = urlencode({'returnTo': request.build_absolute_uri('/')})
        logout_url = 'https://%s/v2/logout?client_id=%s&%s' % (settings.SOCIAL_AUTH_AUTH0_DOMAIN, settings.SOCIAL_AUTH_AUTH0_KEY, return_to)
        return HttpResponseRedirect(logout_url)
