# -*- coding: utf-8 -*-
import calendar
from datetime import date

from async_messages import messages
from django.conf import settings
from core.models import User
from intervention.models import Intervention, InterventionModification, InterventionLog, InterventionStatus, Zone


def update_intervention(intervention_pk, request):
    params = request.POST.copy()
    intervention = Intervention.objects.get(pk=intervention_pk)
    intervention._old_status_id = intervention.status_id
    intervention._old_assigned_id = intervention.assigned_id
    intervention_save = True

    try:
        intervention.status_id = int(params.getlist('intervention_status')[0])
        if int(params.getlist('intervention_status')[0]) != settings.ASSIGNED_STATUS:
            intervention.assigned = None
        else:
            intervention.assigned_id = int(params.getlist('intervention_assigned')[0])
    except IndexError:
        pass

    try:
        intervention.zone_id = int(params.getlist('intervention_zone')[0])
    except IndexError:
        pass

    try:
        modification_text = params.getlist('intervention_modification')[0]
        modification = InterventionModification(intervention=intervention, note=modification_text,
                                                created_by=request.user)
        modification.save()
        intervention_save = False
    except IndexError:
        pass

    try:
        user_to_send = User.objects.get(pk=int(params.getlist('user_to_send')[0]))
        intervention.send_to_user(user_to_send)
        intervention_save = False
    except IndexError:
        pass

    if intervention_save:
        intervention._current_user = request.user
        intervention.save()

    messages.success(request.user, "Modificación realizada correctamente")


def generate_data_year_vs():
    months = ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octube",
              "Noviembre", "Diciembre"]
    data = []
    year = date.today().year.real
    last_year = year - 1
    for x in range(12):
        month = x + 1
        month_str = months[x]
        current_year_count = Intervention.objects.filter(date__year=year, date__month=month).count()
        last_year_count = Intervention.objects.filter(date__year=last_year, date__month=month).count()
        data.append({"y": month_str, "a": current_year_count, "b": last_year_count})

    labels = ["Año " + str(year), "Año " + str(last_year)]

    return {"d": data, "labels": labels}


def generate_data_intervention_input(month=None, year=None):
    data = []

    if month is None or year is None:
        current_date = date.today()
    else:
        current_date = date(year=int(year), month=int(month), day=1)

    max_num = calendar.monthrange(current_date.year, current_date.month)[1].real
    for i in range(max_num):
        day = i + 1
        d = date(current_date.year, current_date.month, day)
        total = Intervention.objects.filter(date__day=day, date__year=d.year.real, date__month=d.month.real).count()
        data.append({'t': total, 'y': d.strftime("%Y-%m-%d")})

    return data


def generate_data_intervention_assigned():
    users = User.objects.all()
    data = []
    for u in users:
        logs = InterventionLog.objects.filter(assigned=u, date__month=date.today().month,
                                              date__year=date.today().year).count()
        if logs > 0:
            data.append({"label": u.get_full_name(), "value": logs})

    return data


def prepare_intervention_modify(intervention_pk, request, status):
    intervention = Intervention.objects.get(pk=intervention_pk)
    intervention._old_status_id = intervention.status_id
    intervention._old_assigned_id = intervention.assigned_id
    intervention._current_user = request.user
    intervention.assigned = None
    intervention.status_id = status
    intervention.save()
    return intervention


def terminate_intervention(intervention_pk, request):
    intervention = prepare_intervention_modify(intervention_pk, request, 3)
    messages.success(request.user, "Avería " + str(intervention) + " marcada como terminada")


def bill_intervention(intervention_pk, request):
    intervention = prepare_intervention_modify(intervention_pk, request, 5)
    messages.success(request.user, "Avería " + str(intervention) + " marcada para facturar")


def get_intervention_list(status_id, user_id, zone_id, starred):
    search_user = None
    search_zone = None

    # NO USER NO ZONE
    if user_id == 0 and zone_id == 0:
        interventions = Intervention.objects.filter(status=status_id).order_by("-date")
    # NO USER WITH ZONE
    elif user_id == 0 and zone_id != 0:
        interventions = Intervention.objects.filter(status=status_id, zone=zone_id).order_by("-date")
        try:
            search_zone = Zone.objects.get(pk=zone_id)
        except Zone.DoesNotExist:
            pass
    # USER WITH NO ZONE
    elif user_id != 0 and zone_id == 0:
        interventions = Intervention.objects.filter(status=status_id, assigned=user_id).order_by("-date")
        try:
            search_user = User.objects.get(pk=user_id)
        except User.DoesNotExist:
            pass
    # USER AND ZONE
    elif user_id != 0 and zone_id != 0:
        interventions = Intervention.objects.filter(status=status_id, zone=zone_id, assigned=user_id).order_by("-date")
        try:
            search_user = User.objects.get(pk=user_id)
        except User.DoesNotExist:
            pass
        try:
            search_zone = Zone.objects.get(pk=zone_id)
        except Zone.DoesNotExist:
            pass

    if starred:
        interventions = interventions.filter(starred=True)

    try:
        search_status = InterventionStatus.objects.get(pk=status_id)
    except InterventionStatus.DoesNotExist:
        search_status = None

    return {'interventions': interventions, 'search_status': search_status, 'search_user': search_user,
            'search_zone': search_zone}
