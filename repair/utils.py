import uuid
import xlwt
from datetime import datetime
from django.db.models import Count
from django.db.models import Q
from django.conf import settings
from django.http import HttpResponse
import qrcode
import qrcode.image.svg
from io import BytesIO

from repair.models import AthRepair, RepairStatus, ZodiacRepair, RepairType, IdegisRepair, AthRepairLog, ZodiacRepairLog, \
    IdegisRepairLog, Repair


def add_list_filters(repair_class, status, starred, budget):

    # Con presupuesto
    if budget == 1:
        repairs = repair_class.objects.annotate(num_b=Count('budgetrepair')).filter(Q(num_b__gt=0) | Q(budget__isnull=False))
    # Sin presupuesto
    elif budget == 2:
        repairs = repair_class.objects.annotate(num_b=Count('budgetrepair')).filter(num_b=0, budget__isnull=True)
    else:
        repairs = repair_class.objects.all()

    if starred:
        repairs = repairs.filter(starred=True)

    if status != 0:
        repairs = repairs.filter(status_id=status)

    return repairs


def generate_repair_qr_code(online_id):
    factory = qrcode.image.svg.SvgImage
    img = qrcode.make(settings.CUSTOMER_REPAIR_URL + str(online_id), image_factory=factory, box_size=6)
    stream = BytesIO()
    img.save(stream)
    return stream.getvalue().decode()


def get_repair_by_type(pk, type) -> Repair:
    if type == RepairType.ATH:
        return AthRepair.objects.get(pk=pk)
    elif type == RepairType.ZODIAC:
        return ZodiacRepair.objects.get(pk=pk)
    elif type == RepairType.IDEGIS:
        return IdegisRepair.objects.get(pk=pk)
    else:
        raise NotImplementedError()


def add_repair_to_intervention(repair, intervention):
    type = repair.type
    if type == RepairType.ATH:
        intervention.repairs_ath.add(repair)
    elif type == RepairType.ZODIAC:
        intervention.repairs_zodiac.add(repair)
    elif type == RepairType.IDEGIS:
        intervention.repairs_idegis.add(repair)
    else:
        raise NotImplementedError()


def remove_repair_from_intervention(repair, intervention):
    type = repair.type
    if type == RepairType.ATH:
        intervention.repairs_ath.remove(repair)
    elif type == RepairType.ZODIAC:
        intervention.repairs_zodiac.remove(repair)
    elif type == RepairType.IDEGIS:
        intervention.repairs_idegis.remove(repair)
    else:
        raise NotImplementedError()


def add_log_to_repair(repair, st_id):
    type = repair.type
    if type == RepairType.ATH:
        return AthRepairLog(status_id=st_id, repair=repair)
    elif type == RepairType.ZODIAC:
        return ZodiacRepairLog(status_id=st_id, repair=repair)
    elif type == RepairType.IDEGIS:
        return IdegisRepairLog(status_id=st_id, repair=repair)
    else:
        raise NotImplementedError()


def get_repair_view_by_type(type):
    if type == RepairType.ATH:
        return 'repair:repair-ath-view'
    elif type == RepairType.ZODIAC:
        return 'repair:repair-zodiac-view'
    elif type == RepairType.IDEGIS:
        return 'repair:repair-idegis-view'
    else:
        raise NotImplementedError()


def generate_report(request):
    from django.db import connection
    response = HttpResponse(content_type='application/ms-excel')
    name = '"informe-reparaciones-'+uuid.uuid1().__str__()+'.xls"'
    response['Content-Disposition'] = 'attachment; filename='+name
    columns = ['ID', 'TIPO', 'MODELO', 'FECHA', 'PRESUPUESTOS', 'ESTADO', 'CLIENTE']

    ath_query = """
        SELECT ra.id, 'ATH' as type, ra.model as model, ra.date as date, count(br.*) as brp, ra.status_id as status_id, cc.name from repair_athrepair ra
        LEFT JOIN budget_budgetrepair br ON br.ath_repair_id = ra.id
        INNER JOIN client_address ca ON ca.id = ra.address_id
        INNER JOIN client_client cc ON cc.id = ca.client_id %s
        GROUP BY ra.id, cc.name %s
        """

    idegis_query = """
        SELECT ri.id, 'IDEGIS' as type, ri.model model, ri.date as date, count(br.*) as brp, ri.status_id as status_id, cc.name from repair_idegisrepair ri
        LEFT JOIN budget_budgetrepair br ON br.idegis_repair_id = ri.id
        INNER JOIN client_address ca ON ca.id = ri.address_id
        INNER JOIN client_client cc ON cc.id = ca.client_id %s
        GROUP BY ri.id, cc.name %s
        """

    zodiac_query = """
        SELECT rz.id, 'FLUIDRA' as type, rz.model as model, rz.date as date, count(br.*) as brp, rz.status_id as status_id, cc.name from repair_zodiacrepair rz
        LEFT JOIN budget_budgetrepair br ON br.zodiac_repair_id = rz.id
        INNER JOIN client_address ca ON ca.id = rz.address_id
        INNER JOIN client_client cc ON cc.id = ca.client_id %s
        GROUP BY rz.id, cc.name %s
        """

    order_and_group = """
                    ORDER BY date desc
    """

    type = int(request.POST.get('providertype', 0))

    selected_queries = []

    if type != 0:
        provider_types = request.POST.getlist("providertype[]")
        if len(provider_types) != 0:
            if 'ath' in provider_types:
                selected_queries.append(_enrich_query(request, ath_query, "ra"))
            if 'idegis' in provider_types:
                selected_queries.append(_enrich_query(request, idegis_query, "ri"))
            if 'zodiac' in provider_types:
                selected_queries.append(_enrich_query(request, zodiac_query, "rz"))
    else:
        selected_queries = [
            _enrich_query(request, ath_query, "ra"),
            _enrich_query(request, idegis_query, "ri"),
            _enrich_query(request, zodiac_query, "rz")
        ]
            
    final_query = " UNION ".join(selected_queries) + order_and_group

    wb = xlwt.Workbook(encoding='utf-8')
    ws = wb.add_sheet('INFORME')
    # Sheet header, first row
    row_num = 0

    font_style = xlwt.XFStyle()
    font_style.font.bold = True

    status_map = {}
    for s in RepairStatus.objects.all():
        status_map[s.pk] = s.name

    for col_num in range(len(columns)):
        ws.write(row_num, col_num, columns[col_num], font_style)

    font_style = xlwt.XFStyle()
    with connection.cursor() as cursor:
        cursor.execute(final_query)
        for row in cursor.fetchall():
            row_num += 1
            ws.write(row_num, 0, _get_id(str(row[1]), row[0]), font_style)
            ws.write(row_num, 1, str(row[1]), font_style)
            ws.write(row_num, 2, str(row[2]), font_style)
            ws.write(row_num, 3, str(row[3]), font_style)
            ws.write(row_num, 4, str(row[4]), font_style)
            ws.write(row_num, 5, status_map[int(row[5])], font_style)
            ws.write(row_num, 6, str(row[6]), font_style)

    wb.save(response)
    return response


def _get_id(type, id):
    if type == "ATH":
        return "A" + str(id)
    elif type == "FLUIDRA":
        return "Z" + str(id)
    elif type == "IDEGIS":
        return "X" + str(id)
    else:
        raise NotImplementedError()


def _enrich_query(request, query, table_alias):
    where_clauses = []
    having_clause = ""
    date = int(request.POST.get('date', 0))
    status = int(request.POST.get('status', 0))
    has_quote = int(request.POST.get('hasquote', 0))

    if status != 0:
        statuses = [int(x) for x in request.POST.getlist("status_pk[]")]
        if len(statuses) != 0:
            status_ids = ",".join(str(id) for id in statuses)
            where_clauses.append("status_id IN (%s)" % status_ids)

    if has_quote != 0:
        if has_quote == 1:
            having_clause = " HAVING count(br.*) > 0"
        if has_quote == 2:
            having_clause = " HAVING count(br.*) < 1"

    if date != 0:
        date1 = request.POST.get('date1', "")
        date2 = request.POST.get('date2', "")
        if date1 != "" and date2 != "":
            date1 = datetime.strptime(date1, "%Y-%m-%d").date()
            date2 = datetime.strptime(date2, "%Y-%m-%d").date()
            where_clauses.append(
                "%s.date BETWEEN '%s'::DATE AND '%s'::DATE" % (table_alias, date1, date2))

    where_clause = ""
    if len(where_clauses) > 0:
        where_clause = " WHERE " + " AND ".join(where_clauses)
  
    return query % (where_clause, having_clause)
