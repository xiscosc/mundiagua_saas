from django.db.models import Count
from django.db.models import Q


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