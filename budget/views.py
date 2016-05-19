# -*- coding: utf-8 -*-
from async_messages import message_user, constants
from django.conf import settings
from django.core.paginator import Paginator
from django.core.urlresolvers import reverse_lazy
from django.db.models import Q
from django.http import HttpResponseRedirect, JsonResponse, Http404
from django.views.generic import TemplateView, View, UpdateView

from budget.models import BudgetStandard, BudgetLineStandard
from core.views import SearchClientBaseView, CreateBaseView


class SearchClientView(SearchClientBaseView):
    def get_context_data(self, **kwargs):
        context = super(SearchClientView, self).get_context_data(**kwargs)
        context['title'] = "Nuevo presupuesto"
        context['new_url'] = "budget:budget-new"
        context['btn_text'] = "Crear presupuesto"
        context['btn_class'] = "btn-warning"
        return context


class CreateBudgetView(CreateBaseView):
    model = BudgetStandard
    fields = ['address', 'introduction', 'conditions', 'tax']

    def get_context_data(self, **kwargs):
        context = super(CreateBudgetView, self).get_context_data(**kwargs)
        context['title'] = "Nuevo presupuesto"
        context['subtitle'] = "Datos del presupuesto"
        return context

    def get_success_url(self):
        return reverse_lazy("budget:budget-new-lines", kwargs={'pk': self.object.pk})


class CreateLineBudgetView(TemplateView):
    template_name = "lines_budget.html"

    def get_context_data(self, **kwargs):
        context = super(CreateLineBudgetView, self).get_context_data(**kwargs)
        context['budget'] = BudgetStandard.objects.get(pk=kwargs['pk'])
        return context

    def post(self, request, *args, **kwargs):
        params = request.POST.copy()
        products = params.getlist('product')
        dtos = [d.replace(',', '.') for d in params.getlist('dto')]
        prices = [d.replace(',', '.') for d in params.getlist('price')]
        quantities = [d.replace(',', '.') for d in params.getlist('quantity')]

        for x in range(len(products)):
            line = BudgetLineStandard(product=products[x], discount=dtos[x], quantity=quantities[x],
                                      unit_price=prices[x], budget_id=kwargs['pk'])
            line.save()

        return HttpResponseRedirect(reverse_lazy("budget:budget-view", kwargs={'pk': kwargs['pk']}))


class TypeAheadBudgetView(View):
    def dispatch(self, request, *args, **kwargs):
        if not request.is_ajax():
            raise Http404("This is an ajax view, friend.")
        return super(TypeAheadBudgetView, self).dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        data = []
        lines = BudgetLineStandard.objects.all()
        for l in lines:
            data.append(l.product)
        return JsonResponse(data=list(set(data)), safe=False)


class BudgetDetailView(UpdateView):
    model = BudgetStandard
    template_name = "detail_budget.html"
    fields = ['introduction', 'conditions', 'tax', "invalid"]
    context_object_name = "budget"

    def get_success_url(self):
        return reverse_lazy("budget:budget-view", kwargs={'pk': self.object.pk})

    def form_valid(self, form):
        message_user(self.request.user, "Presupuesto actualizado correctamente.", constants.SUCCESS)
        return super(BudgetDetailView, self).form_valid(form)


class EditLineBudgetView(TemplateView):
    template_name = "lines_budget_edit.html"

    def get_context_data(self, **kwargs):
        context = super(EditLineBudgetView, self).get_context_data(**kwargs)
        context['budget'] = BudgetStandard.objects.get(pk=kwargs['pk'])
        return context

    def post(self, request, *args, **kwargs):
        params = request.POST.copy()
        pk_lines = params.getlist('pk_line')
        products = params.getlist('product')
        dtos = [d.replace(',', '.') for d in params.getlist('dto')]
        prices = [d.replace(',', '.') for d in params.getlist('price')]
        quantities = [d.replace(',', '.') for d in params.getlist('quantity')]
        pk_created = []

        for x in range(len(products)):

            if int(pk_lines[x]) == 0:
                line = BudgetLineStandard(product=products[x], discount=dtos[x], quantity=quantities[x],
                                          unit_price=prices[x], budget_id=kwargs['pk'])
                line.save()
                pk_created.append(line.pk)
            else:
                line = BudgetLineStandard.objects.get(pk=int(pk_lines[x]))
                line.product = products[x]
                line.discount = dtos[x]
                line.quantity = quantities[x]
                line.unit_price = prices[x]
                line.save()

            deleted_lines = BudgetLineStandard.objects.filter(budget_id=kwargs['pk']).exclude(
                pk__in=(pk_lines + pk_created))
            deleted_lines.delete()

        message_user(request.user, "Contenido del presupuesto actualizado correctamente.", constants.SUCCESS)
        return HttpResponseRedirect(reverse_lazy("budget:budget-view", kwargs={'pk': kwargs['pk']}))


class ListBudgetView(TemplateView):
    template_name = "list_budget.html"

    def get_context_data(self, **kwargs):
        context = super(ListBudgetView, self).get_context_data(**kwargs)
        page = int(self.request.GET.get('page', 1))
        budgets = BudgetStandard.objects.all().order_by("-date")
        paginator = Paginator(budgets, settings.DEFAULT_BUDGETS_PAGINATOR)
        context['budgets'] = paginator.page(page)
        return context


class PreSearchBudgetView(View):
    def post(self, request, *args, **kwargs):
        params = request.POST.copy()
        search_text = params.getlist('search_text')[0]

        budgets = BudgetStandard.objects.filter(
            Q(address__client__name__icontains=search_text) | Q(
                address__address__icontains=search_text))

        pk_list = []
        for i in budgets:
            pk_list.append(i.pk)

        request.session['search_budgets'] = pk_list
        request.session['search_budgets_text'] = search_text
        return HttpResponseRedirect(reverse_lazy('budget:budget-search'))


class SearchBudgetView(TemplateView):
    template_name = "list_budget.html"

    def get_context_data(self, **kwargs):
        context = super(SearchBudgetView, self).get_context_data(**kwargs)
        page = int(self.request.GET.get('page', 1))
        search_text = str(self.request.session.get('search_budgets_text', ""))
        context['title'] = "Búsqueda - " + search_text
        budgets_pk = self.request.session.get('search_budgets', list())
        budgets = BudgetStandard.objects.filter(pk__in = budgets_pk).order_by("-date")
        paginator = Paginator(budgets, settings.DEFAULT_BUDGETS_PAGINATOR)
        context['budgets'] = paginator.page(page)
        return context
