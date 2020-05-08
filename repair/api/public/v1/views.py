from django.http import Http404
from django.shortcuts import get_object_or_404
from rest_framework import viewsets
from rest_framework.response import Response

from repair.api.public.v1.serializers import AthRepairSerializer, IdegisRepairSerializer
from repair.models import AthRepair, IdegisRepair

class RepairStatusViewSet(viewsets.ViewSet):
    def retrieve(self, request, pk=None):
        first_letter = pk[:1].upper()
        if first_letter == 'X':
            queryset = IdegisRepair.objects.all()
            repair = get_object_or_404(queryset, online_id=pk)
            serializer = IdegisRepairSerializer(repair)
        elif first_letter == 'A':
            queryset = AthRepair.objects.all()
            repair = get_object_or_404(queryset, online_id=pk)
            serializer = AthRepairSerializer(repair)
        else:
            raise Http404

        return Response(serializer.data)
