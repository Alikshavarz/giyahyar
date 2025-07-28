from rest_framework import serializers
from .models import SubscriptionPlan, Subscription, PaymentHistory, Notification

class SubscriptionPlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubscriptionPlan
        fields = ['id', 'name', 'duration_days', 'price', 'description']

class SubscriptionSerializer(serializers.ModelSerializer):
    plan = SubscriptionPlanSerializer()
    class Meta:
        model = Subscription
        fields = ['id', 'plan', 'start_at', 'expire_at', 'is_active']

class PaymentHistorySerializer(serializers.ModelSerializer):
    plan = SubscriptionPlanSerializer()
    class Meta:
        model = PaymentHistory
        fields = ['id', 'plan', 'amount', 'is_successful', 'created_at', 'ref_id', 'fail_reason']

class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = ['id', 'message', 'created_at', 'is_read']
        
        
        

