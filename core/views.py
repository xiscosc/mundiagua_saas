from django.core.paginator import Paginator
from django.urls import reverse_lazy
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.conf import settings
from django.views.generic import TemplateView
from django.views.generic.base import View
from django.views.generic.edit import CreateView, UpdateView
from django.contrib.auth import login
from django.contrib.auth.views import LoginView
from oauth2client import client
from client.models import Client, Address
from core.forms import SystemVariableRichForm, SystemVariablePlainForm
from core.models import User, Message, SystemVariable
from core.utils import get_return_from_id, has_to_change_password
from engine.models import EngineRepair, EngineStatus
from repair.models import RepairStatus


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
            if not request.user.is_google and has_to_change_password(request.user.last_password_update) is True:
                response = 'password-change'
            else:
                if request.user.is_officer:
                    response = 'intervention:intervention-home'
                else:
                    response = 'intervention:intervention-list-own'
        else:
            response = 'login'
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
        context['messages_mundiagua'] = paginator.page(page)
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
        context['intranet_version'] = settings.APP_COMPLETE_VERSION
        context['django_version'] = django.__version__
        context['amazon_version'] = boto3.__version__
        context['sendgrid_version'] = sendgrid.__version__
        context['celery_version'] = celery.__version__
        context['python_version'] = sys.version
        context['memcache_version'] = memcache.__version__
        context['postgre_version_c'] = psycopg2.__version__
        context['postgre_version'] = psycopg2.__libpq_version__
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


class UserView(TemplateView):
    template_name = 'user.html'

    def get_context_data(self, **kwargs):
        context = super(UserView, self).get_context_data(**kwargs)
        context['telegran_name'] = settings.TELEGRAM_NAME
        return context


class GoogleLoginView(TemplateView):
    template_name = 'login_google.html'


class GoogleErrorView(TemplateView):
    template_name = 'error_google.html'


class GoogleProcessView(View):

    def get(self, request, *args, **kwargs):
        return HttpResponseRedirect(reverse_lazy('home'))

    def post(self, request, *args, **kwargs):
        params = request.POST.copy()
        token = params.getlist('token')[0]
        try:
            next = params.getlist('next')[0]
        except:
            next = False
        idinfo = client.verify_id_token(token, settings.GOOGLE_CLIENT_ID)
        try:
            user = User.objects.get(email=idinfo['email'])
            if user.is_active and user.is_google:
                login(user=user, request=request, backend=None)
                if next:
                    return HttpResponseRedirect(next)
                else:
                    return HttpResponseRedirect(reverse_lazy('home'))
            else:
                return HttpResponseRedirect(reverse_lazy('login-google-error'))
        except User.DoesNotExist:
            return HttpResponseRedirect(reverse_lazy('login-google-error'))


class LoginRedirectView(View):

    def get(self, request, *args, **kwargs):
        url = reverse_lazy('login-google')
        next = request.GET.get('next', "/")
        return HttpResponseRedirect(url+"?next="+next)


class LoginPasswordView(LoginView):

    def dispatch(self, request, *args, **kwargs):

        if request.user.is_authenticated:
            next = request.GET.get('next', "/")
            return HttpResponseRedirect(next)
        else:
            return super(LoginPasswordView, self).dispatch(request, *args, **kwargs)
