from django.http import Http404
from django.shortcuts import get_object_or_404
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.decorators import permission_classes
from rest_framework.permissions import AllowAny

from repair.api.public.v1.serializers import AthRepairSerializer, IdegisRepairSerializer, ZodiacRepairSerializer
from repair.models import AthRepair, IdegisRepair, ZodiacRepair


@permission_classes([AllowAny])
class RepairStatusViewSet(viewsets.ViewSet):
    def retrieve(self, request, pk=None):
        first_letter = pk[:1].upper()
        if first_letter == 'X':
            queryset = IdegisRepair.objects.all()
            repair = get_object_or_404(queryset, online_id__iexact=pk)
            serializer = IdegisRepairSerializer(repair)
        elif first_letter == 'A':
            queryset = AthRepair.objects.all()
            repair = get_object_or_404(queryset, online_id__iexact=pk)
            serializer = AthRepairSerializer(repair)
        elif first_letter == 'Z':
            queryset = ZodiacRepair.objects.all()
            repair = get_object_or_404(queryset, online_id__iexact=pk)
            serializer = ZodiacRepairSerializer(repair)
        else:
            raise Http404

        return Response(serializer.data)
