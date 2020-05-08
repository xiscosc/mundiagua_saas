from rest_framework import serializers
from repair.models import AthRepair, IdegisRepair, RepairStatus, AthRepairLog, IdegisRepairLog


class RepairStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = RepairStatus
        fields = ['name', 'description', 'percentage']


class AthLogStatusSerializer(serializers.ModelSerializer):
    status = RepairStatusSerializer(read_only=True)

    class Meta:
        model = AthRepairLog
        fields = ['date', 'status']


class IdegisLogStatusSerializer(serializers.ModelSerializer):
    status = RepairStatusSerializer(read_only=True)

    class Meta:
        model = IdegisRepairLog
        fields = ['date', 'status']


class AthRepairSerializer(serializers.ModelSerializer):
    status = RepairStatusSerializer(read_only=True)
    history = AthLogStatusSerializer(read_only=True, many=True, source='athrepairlog_set')

    class Meta:
        model = AthRepair
        fields = ['private_id', 'online_id', 'type', 'model', 'warranty', 'date', 'status', 'history']


class IdegisRepairSerializer(serializers.HyperlinkedModelSerializer):
    status = RepairStatusSerializer(read_only=True)
    history = IdegisLogStatusSerializer(read_only=True, many=True, source='idegisrepairlog_set')

    class Meta:
        model = IdegisRepair
        fields = ['private_id', 'online_id', 'type', 'model', 'warranty', 'date', 'status', 'history']
