from django.db.models import Count


def add_list_filters(repair_class, status, starred, budget):

    # Con presupuesto
    if budget == 1:
        repairs = repair_class.objects.annotate(num_b=Count('budgetrepair')).filter(num_b__gt=0)
    # Sin presupuesto
    elif budget == 2:
        repairs = repair_class.objects.annotate(num_b=Count('budgetrepair')).filter(num_b=0)
    else:
        repairs = repair_class.objects.all()

    if starred:
        repairs = repairs.filter(starred=True)

    if status != 0:
        repairs = repairs.filter(status_id=status)

    return repairs