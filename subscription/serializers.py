from rest_framework import serializers
from .models import Plan, Subscription, PaymentHistory

class PlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = Plan
        fields = ['id', 'name', 'description', 'duration_days', 'price']

class SubscriptionSerializer(serializers.ModelSerializer):
    plan = PlanSerializer(read_only=True)
    plan_id = serializers.PrimaryKeyRelatedField(
        queryset=Plan.objects.filter(is_active=True),
        source='plan', write_only=True
    )
    class Meta:
        model = Subscription
        fields = ['id', 'user', 'plan', 'plan_id', 'started_at', 'expired_at', 'is_active', 'auto_renew']
        read_only_fields = ['id', 'user', 'started_at', 'expired_at', 'is_active']

class PaymentHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentHistory
        fields = "__all__"
        read_only_fields = ["id", "pay_time", "user", "subscription"]
