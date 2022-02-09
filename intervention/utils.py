# -*- coding: utf-8 -*-
import calendar
from tokenize import group
import xlwt
import uuid
import os
from datetime import date, datetime
from functools import reduce

from async_messages import messages
from django.conf import settings
from django.http import HttpResponse

from core.models import User
from intervention.models import Intervention, InterventionModification, InterventionLog, InterventionStatus, Zone, Tag
from intervention.tasks import send_intervention


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
            intervention.assigned_id = int(
                params.getlist('intervention_assigned')[0])
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
        pktosend = int(params.getlist('user_to_send')[0])
        send_intervention(intervention.pk, pktosend, request.user.pk)
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
        current_year_count = Intervention.objects.filter(
            date__year=year, date__month=month).count()
        last_year_count = Intervention.objects.filter(
            date__year=last_year, date__month=month).count()
        data.append(
            {"y": month_str, "a": current_year_count, "b": last_year_count})

    labels = ["Año " + str(year), "Año " + str(last_year)]

    return {"d": data, "labels": labels}


def generate_data_intervention_input(month=None, year=None):
    data = []

    if month is None or year is None:
        current_date = date.today()
    else:
        current_date = date(year=int(year), month=int(month), day=1)

    max_num = calendar.monthrange(
        current_date.year, current_date.month)[1].real
    for i in range(max_num):
        day = i + 1
        d = date(current_date.year, current_date.month, day)
        total = Intervention.objects.filter(
            date__day=day, date__year=d.year.real, date__month=d.month.real).count()
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
    messages.success(request.user, "Avería " +
                     str(intervention) + " marcada como terminada")


def bill_intervention(intervention_pk, request):
    intervention = prepare_intervention_modify(intervention_pk, request, 5)
    messages.success(request.user, "Avería " +
                     str(intervention) + " marcada para facturar")


def get_intervention_list(status_id, user_id, zone_id, starred, tag_id):
    search_user = None
    search_zone = None
    search_tag = None

    # NO USER NO ZONE
    if user_id == 0 and zone_id == 0:
        interventions = Intervention.objects.filter(
            status=status_id).order_by("-date")
    # NO USER WITH ZONE
    elif user_id == 0 and zone_id != 0:
        interventions = Intervention.objects.filter(
            status=status_id, zone=zone_id).order_by("-date")
        try:
            search_zone = Zone.objects.get(pk=zone_id)
        except Zone.DoesNotExist:
            pass
    # USER WITH NO ZONE
    elif user_id != 0 and zone_id == 0:
        interventions = Intervention.objects.filter(
            status=status_id, assigned=user_id).order_by("-date")
        try:
            search_user = User.objects.get(pk=user_id)
        except User.DoesNotExist:
            pass
    # USER AND ZONE
    elif user_id != 0 and zone_id != 0:
        interventions = Intervention.objects.filter(
            status=status_id, zone=zone_id, assigned=user_id).order_by("-date")
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

    if tag_id > 0:
        search_tag = Tag.objects.get(pk=tag_id)
        interventions = interventions.filter(tags=search_tag)

    try:
        search_status = InterventionStatus.objects.get(pk=status_id)
    except InterventionStatus.DoesNotExist:
        search_status = None

    return {'interventions': interventions, 'search_status': search_status, 'search_user': search_user,
            'search_zone': search_zone, 'search_tag': search_tag}


def generate_document_s3_key(intervention: Intervention, filename):
    folder = intervention.__str__()
    id = uuid.uuid1().__str__()
    _, file_extension = os.path.splitext(filename)
    return "%s/%s%s" % (folder, id, file_extension)


def generate_report(request):
    from django.db import connection
    response = HttpResponse(content_type='application/ms-excel')
    name = '"informe-'+uuid.uuid1().__str__()+'.xls"'
    response['Content-Disposition'] = 'attachment; filename='+name
    columns = ['ID', 'CLIENTE', 'FECHA',
               'DESCRIPCION', 'ESTADO', 'ETIQUETAS', "ZONA"]

    date = int(request.POST.get('date', 0))
    worker = int(request.POST.get('worker', 0))
    zone = int(request.POST.get('zone', 0))
    status = int(request.POST.get('status', 0))
    select = """
                SELECT ii.id, min(cc."name") as customer_name, ii."date", short_description, min(iis."name") as status, string_agg(it."name", ', ') as tags, min(iz."name") as zone FROM intervention_intervention ii
                    INNER JOIN client_address ca ON ii.address_id = ca.id
                    INNER JOIN client_client cc ON cc.id = ca.client_id
                    INNER JOIN intervention_zone iz ON ii.zone_id = iz.id
                    INNER JOIN intervention_interventionstatus iis ON iis.id = ii.status_id
                    LEFT JOIN intervention_intervention_tags iit ON iit.intervention_id = ii.id
                    LEFT JOIN intervention_tag it ON it.id = iit.tag_id 
    """

    order_and_group = """
                    GROUP BY ii.id
                    ORDER BY ii.id ASC
    """

    where_clauses = []

    if worker is not 0:
        workers = [int(x) for x in request.POST.getlist("worker_pk[]")]
        if len(workers) is not 0:
            worker_ids = ",".join(str(id) for id in workers)
            select += " LEFT JOIN intervention_interventionlog iil ON ii.id = iil.intervention_id  "
            where_clauses.append("iil.assigned_id IN (%s)" % worker_ids)

    if zone is not 0:
        zones = [int(x) for x in request.POST.getlist("zone_pk[]")]
        if len(zones) is not 0:
            zone_ids = ",".join(str(id) for id in zones)
            where_clauses.append("iz.id IN (%s)" % zone_ids)

    if status is not 0:
        statuses = [int(x) for x in request.POST.getlist("status_pk[]")]
        if len(statuses) is not 0:
            status_ids = ",".join(str(id) for id in statuses)
            where_clauses.append("iis.id IN (%s)" % status_ids)

    if date is not 0:
        date1 = request.POST.get('date1', "")
        date2 = request.POST.get('date2', "")
        if date1 is not "" and date2 is not "":
            date1 = datetime.strptime(date1, "%Y-%m-%d").date()
            date2 = datetime.strptime(date2, "%Y-%m-%d").date()
            where_clauses.append(
                "ii.date BETWEEN '%s'::DATE AND '%s'::DATE" % (date1, date2))

    query = select
    if len(where_clauses) > 0:
        query += " WHERE " + " AND ".join(where_clauses)

    query += order_and_group
    wb = xlwt.Workbook(encoding='utf-8')
    ws = wb.add_sheet('INFORME')
    # Sheet header, first row
    row_num = 0

    font_style = xlwt.XFStyle()
    font_style.font.bold = True

    for col_num in range(len(columns)):
        ws.write(row_num, col_num, columns[col_num], font_style)

    font_style = xlwt.XFStyle()
    with connection.cursor() as cursor:
        cursor.execute(query)
        for row in cursor.fetchall():
            row_num += 1
            ws.write(row_num, 0, "V" + str(row[0]), font_style)
            ws.write(row_num, 1, str(row[1]), font_style)
            ws.write(row_num, 2, str(row[2]), font_style)
            ws.write(row_num, 3, str(row[3]), font_style)
            ws.write(row_num, 4, str(row[4]), font_style)
            ws.write(row_num, 5, str(row[5]), font_style)
            ws.write(row_num, 6, str(row[6]), font_style)

    wb.save(response)
    return response
