from django.core.management.base import BaseCommand

from client.models import Client
from intervention.models import Intervention
from itertools import groupby


class Command(BaseCommand):
    help = ''

    def handle(self, *args, **options):
        Client.objects.filter(address__pk=None).delete()
        saved = 0
        for client in Client.objects.all():
            for add in client.get_addresses():
                interventions = Intervention.objects.filter(address=add).exclude(zone_id=9)
                if len(interventions) > 0:
                    zones = []
                    for i in interventions:
                        zones.append(i.zone.pk)
                    zones.sort()
                    zones_set = list(set(zones))
                    freq = [len(list(group)) for key, group in groupby(zones)]
                    index_max = freq.index(max(freq))
                    new_zone = zones_set[index_max]
                    if add.default_zone_id is not new_zone:
                        add.default_zone_id = new_zone
                        add.save()
                        saved += 1

        print("UPDATED: " + str(saved))
