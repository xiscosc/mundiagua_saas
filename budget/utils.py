def get_data_typeahead(type):
    data = []
    lines = type.objects.extra(where=["CHAR_LENGTH(product) < 140"])
    for l in lines:
        p = l.product.rstrip(' ')
        p = p.rstrip('.')
        p = p.rstrip(' ')
        data.append(p)
    return data