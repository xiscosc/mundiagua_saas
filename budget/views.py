# -*- coding: utf-8 -*-
from async_messages import message_user, constants
from django.conf import settings
from django.core.paginator import Paginator
from django.core.urlresolvers import reverse_lazy
from django.db.models import Q
from django.http import HttpResponseRedirect, JsonResponse, Http404
from django.views.generic import TemplateView, View, UpdateView, DetailView
from wkhtmltopdf.views import PDFTemplateView

from budget.models import BudgetStandard, BudgetLineStandard, BudgetRepair, BudgetLineRepair
from core.views import SearchClientBaseView, CreateBaseView, PreSearchView, DefaultPDFView
from repair.models import AthRepair, IdegisRepair


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
        lines = BudgetLineStandard.objects.extra(where=["CHAR_LENGTH(product) < 140"])
        for l in lines:
            data.append(l.product)
        lines2 = BudgetLineRepair.objects.extra(where=["CHAR_LENGTH(product) < 140"])
        for l in lines2:
            data.append(l.product)
        return JsonResponse(data=list(set(data)), safe=False)


class BudgetDetailBase(UpdateView):
    template_name = "detail_budget.html"
    fields = ['introduction', 'conditions', 'tax', "invalid"]
    context_object_name = "budget"

    def form_valid(self, form):
        message_user(self.request.user, "Presupuesto actualizado correctamente.", constants.SUCCESS)
        return super(BudgetDetailBase, self).form_valid(form)


class BudgetDetailView(BudgetDetailBase):
    model = BudgetStandard

    def get_success_url(self):
        return reverse_lazy("budget:budget-view", kwargs={'pk': self.object.pk})


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


class PreSearchBudgetView(PreSearchView):
    def set_data_and_response(self, request):
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
        budgets = BudgetStandard.objects.filter(pk__in=budgets_pk).order_by("-date")
        paginator = Paginator(budgets, settings.DEFAULT_BUDGETS_PAGINATOR)
        context['budgets'] = paginator.page(page)
        return context


class ListBudgetRepairView(TemplateView):
    template_name = "list_budget.html"

    def get_context_data(self, **kwargs):
        context = super(ListBudgetRepairView, self).get_context_data(**kwargs)
        page = int(self.request.GET.get('page', 1))

        if int(kwargs['type']) == 1:
            context['title'] = "Presupuestos de  A" + kwargs['pk']
            budgets = BudgetRepair.objects.filter(ath_repair_id=kwargs['pk']).order_by("-intern_id")
        else:
            context['title'] = "Presupuestos de  X" + kwargs['pk']
            budgets = BudgetRepair.objects.filter(idegis_repair_id=kwargs['pk']).order_by("-intern_id")

        paginator = Paginator(budgets, settings.DEFAULT_BUDGETS_PAGINATOR)
        context['budgets'] = paginator.page(page)
        return context


class CreateBudgetRepairView(CreateBaseView):
    model = BudgetRepair
    fields = ['introduction', 'conditions', 'tax']

    def get_context_data(self, **kwargs):
        context = super(CreateBudgetRepairView, self).get_context_data(**kwargs)
        context['is_budget_repair'] = True
        if int(self.kwargs['type']) == 1:
            context['title'] = "Crear presupuesto de  A" + self.kwargs['pk']
            context['repair'] = AthRepair.objects.get(pk=self.kwargs['pk'])
        else:
            context['title'] = "Crear presupuesto de  X" + self.kwargs['pk']
            context['repair'] = IdegisRepair.objects.get(pk=self.kwargs['pk'])
        context['subtitle'] = "Datos del presupuesto"
        return context

    def get_success_url(self):
        return reverse_lazy("budget:budget-repair-new-lines", kwargs={'pk': self.object.pk})

    def form_valid(self, form):
        obj = form.save(commit=False)
        if int(self.kwargs['type']) == 1:
            repair = AthRepair.objects.get(pk=self.kwargs['pk'])
            obj.ath_repair = repair
            try:
                other_b = BudgetRepair.objects.filter(ath_repair_id=self.kwargs['pk']).order_by("-date")[:1]
                next_id = other_b[0].intern_id + 1
                obj.intern_id = next_id
            except:
                pass
        else:
            repair = IdegisRepair.objects.get(pk=self.kwargs['pk'])
            obj.idegis_repair = repair
            try:
                other_b = BudgetRepair.objects.filter(idegis_repair=self.kwargs['pk']).order_by("-date")[:1]
                next_id = other_b[0].intern_id + 1
                obj.intern_id = next_id
            except:
                pass

        obj.address = repair.address
        return super(CreateBudgetRepairView, self).form_valid(form)


class CreateLineBudgetRepairView(TemplateView):
    template_name = "lines_budget.html"

    def get_context_data(self, **kwargs):
        context = super(CreateLineBudgetRepairView, self).get_context_data(**kwargs)
        context['budget'] = BudgetRepair.objects.get(pk=kwargs['pk'])
        return context

    def post(self, request, *args, **kwargs):
        params = request.POST.copy()
        products = params.getlist('product')
        dtos = [d.replace(',', '.') for d in params.getlist('dto')]
        prices = [d.replace(',', '.') for d in params.getlist('price')]
        quantities = [d.replace(',', '.') for d in params.getlist('quantity')]

        for x in range(len(products)):
            line = BudgetLineRepair(product=products[x], discount=dtos[x], quantity=quantities[x],
                                    unit_price=prices[x], budget_id=kwargs['pk'])
            line.save()

        return HttpResponseRedirect(reverse_lazy("budget:budget-repair-view", kwargs={'pk': kwargs['pk']}))


class BudgetRepairDetailView(BudgetDetailBase):
    model = BudgetRepair

    def get_success_url(self):
        return reverse_lazy("budget:budget-repair-view", kwargs={'pk': self.object.pk})

    def get_context_data(self, **kwargs):
        context = super(BudgetRepairDetailView, self).get_context_data(**kwargs)
        context['repair'] = self.object.get_repair()
        return context


class EditLineBudgetRepairView(TemplateView):
    template_name = "lines_budget_edit.html"

    def get_context_data(self, **kwargs):
        context = super(EditLineBudgetRepairView, self).get_context_data(**kwargs)
        context['budget'] = BudgetRepair.objects.get(pk=kwargs['pk'])
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
                line = BudgetLineRepair(product=products[x], discount=dtos[x], quantity=quantities[x],
                                          unit_price=prices[x], budget_id=kwargs['pk'])
                line.save()
                pk_created.append(line.pk)
            else:
                line = BudgetLineRepair.objects.get(pk=int(pk_lines[x]))
                line.product = products[x]
                line.discount = dtos[x]
                line.quantity = quantities[x]
                line.unit_price = prices[x]
                line.save()

            deleted_lines = BudgetLineRepair.objects.filter(budget_id=kwargs['pk']).exclude(
                pk__in=(pk_lines + pk_created))
            deleted_lines.delete()

        message_user(request.user, "Contenido del presupuesto actualizado correctamente.", constants.SUCCESS)
        return HttpResponseRedirect(reverse_lazy("budget:budget-repair-view", kwargs={'pk': kwargs['pk']}))


class BudgetPrintView(TemplateView):
    template_name = 'print_budget.html'

    def get_context_data(self, **kwargs):
        context = super(BudgetPrintView, self).get_context_data(**kwargs)
        context['budget'] = BudgetStandard.objects.get(pk=kwargs['pk'])
        return context


class BudgetRepairPrintView(TemplateView):
    template_name = 'print_budget.html'

    def get_context_data(self, **kwargs):
        context = super(BudgetRepairPrintView, self).get_context_data(**kwargs)
        context['budget'] = BudgetRepair.objects.get(pk=kwargs['pk'])
        return context