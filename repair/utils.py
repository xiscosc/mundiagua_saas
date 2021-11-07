from django.db.models import Count
from django.db.models import Q
from django.conf import settings
import qrcode
import qrcode.image.svg
from io import BytesIO

from repair.models import AthRepair, ZodiacRepair, RepairType, IdegisRepair, AthRepairLog, ZodiacRepairLog


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


def get_repair_by_type(pk, type):
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
        return IdegisRepair(status_id=st_id, repair=repair)
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