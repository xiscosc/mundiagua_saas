def parse_budget_amount(value):
    value = value.replace(',', '.')
    count = value.count('.')
    if count > 1:
        value = value.replace('.', '', count - 1)
    return value
