def get_zone_using_interventions(address):
    from django.db import connection
    select = '''select i.zone_id as zid, count(*) c from client_address a
                inner join intervention_intervention i on i.address_id = a.id
                where address_id = %s
                group by zid
                order by c desc
                limit 1;
                ''' % address.pk

    with connection.cursor() as cursor:
        cursor.execute(select)
        first_row = cursor.fetchone()
        if first_row:
            from intervention.models import Zone
            return Zone.objects.get(pk=first_row[0])
        else:
            return None
