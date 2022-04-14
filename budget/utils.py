from budget.models import (
    BudgetStandard,
    BudgetLineStandard,
    BudgetRepair,
    BudgetLineRepair,
)
from core.models import User


def parse_budget_amount(value: str) -> str:
    value = value.replace(",", ".")
    count = value.count(".")
    if count > 1:
        value = value.replace(".", "", count - 1)
    return value


def duplicate_budget_standard(
    budget: BudgetStandard, new_address_id: int, user: User
) -> BudgetStandard:
    new_budget = BudgetStandard(
        created_by=user,
        introduction=budget.introduction,
        conditions=budget.conditions,
        invalid=budget.invalid,
        address_id=new_address_id,
    )
    new_budget.save()

    for line in budget.get_lines():
        new_line = BudgetLineStandard(
            budget=new_budget,
            product=line.product,
            unit_price=line.unit_price,
            quantity=line.quantity,
            discount=line.discount,
        )
        new_line.save()

    return new_budget


def duplicate_budget_repair(budget: BudgetRepair, user: User) -> BudgetRepair:
    new_budget = BudgetRepair(
        created_by=user,
        introduction=budget.introduction,
        conditions=budget.conditions,
        invalid=budget.invalid,
        address=budget.address,
        idegis_repair=budget.idegis_repair,
        ath_repair=budget.ath_repair,
        zodiac_repair=budget.zodiac_repair,
    )
    new_budget.intern_id = get_current_intern_id(new_budget) + 1
    new_budget.save()

    for line in budget.get_lines():
        new_line = BudgetLineRepair(
            budget=new_budget,
            product=line.product,
            unit_price=line.unit_price,
            quantity=line.quantity,
            discount=line.discount,
        )
        new_line.save()

    return new_budget


def get_current_intern_id(budget: BudgetRepair) -> int:
    if budget.idegis_repair is not None:
        current_id = BudgetRepair.objects.filter(
            idegis_repair=budget.idegis_repair
        ).count()
    elif budget.ath_repair is not None:
        current_id = BudgetRepair.objects.filter(ath_repair=budget.ath_repair).count()
    else:
        current_id = BudgetRepair.objects.filter(
            zodiac_repair=budget.zodiac_repair
        ).count()

    return current_id
