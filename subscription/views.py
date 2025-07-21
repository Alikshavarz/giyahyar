from rest_framework import generics, status, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Plan, Subscription, PaymentHistory
from .serializers import PlanSerializer, SubscriptionSerializer, PaymentHistorySerializer
from django.utils import timezone


class PlanListView(generics.ListAPIView):
    queryset = Plan.objects.filter(is_active=True)
    serializer_class = PlanSerializer
    permission_classes = [permissions.AllowAny]


class SubscriptionListView(generics.ListAPIView):
    serializer_class = SubscriptionSerializer
    permission_classes = [permissions.IsAuthenticated]
    def get_queryset(self):
        return Subscription.objects.filter(user=self.request.user).order_by('-started_at')


class SubscriptionDeleteView(generics.DestroyAPIView):
    serializer_class = SubscriptionSerializer
    permission_classes = [permissions.IsAuthenticated]
    def get_queryset(self):
        return Subscription.objects.filter(user=self.request.user, is_active=True)


class SubscriptionCreateView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    def post(self, request):
        plan_id = request.data.get('plan_id')
        payment_method = request.data.get('payment_method', 'gateway')
        try:
            plan = Plan.objects.get(id=plan_id, is_active=True)
        except Plan.DoesNotExist:
            return Response({'detail':'پلن وجود ندارد.'}, status=400)
        user = request.user
        

        now = timezone.now()
        expired_at = now + timezone.timedelta(days=plan.duration_days)
        sub = Subscription.objects.create(
            user=user, plan=plan, started_at=now, expired_at=expired_at, is_active=True
        )
        PaymentHistory.objects.create(
            user=user, subscription=sub, amount=plan.price, plan_name=plan.name,
            status='success', payment_gateway=payment_method,
            description=f"خرید پلن {plan.name}",
        )
        return Response(SubscriptionSerializer(sub).data, status=201)


class PaymentHistoryListView(generics.ListAPIView):
    serializer_class = PaymentHistorySerializer
    permission_classes = [permissions.IsAuthenticated]
    def get_queryset(self):
        return PaymentHistory.objects.filter(user=self.request.user).order_by('-pay_time')


class SubscriptionStatsView(APIView):
    permission_classes = [permissions.IsAdminUser]
    def get(self, request):
        s_count = Subscription.objects.filter(is_active=True, expired_at__gte=timezone.now()).count()
        p_count = PaymentHistory.objects.filter(status="success").count()
        return Response({
            "active_subscription_count": s_count,
            "total_success_payments": p_count
        })
