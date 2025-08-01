from rest_framework import generics, status, permissions, views
from rest_framework.response import Response
from django.utils import timezone
from .models import Subscription, Plan, PaymentHistory
from .serializers import SubscriptionSerializer, PlanSerializer, PaymentHistorySerializer
from .tasks import send_fcm_notification

class SubscriptionListCreateView(generics.ListCreateAPIView):
    serializer_class = SubscriptionSerializer
    permission_classes = [permissions.IsAuthenticated]
    def get_queryset(self):
        return Subscription.objects.filter(user=self.request.user).order_by('-started_at')
    def create(self, request, *args, **kwargs):
        plan_id = request.data.get("plan_id")
        try:
            plan = Plan.objects.get(id=plan_id, is_active=True)
        except Plan.DoesNotExist:
            return Response({"detail": "پلن وجود ندارد."}, status=400)
        now = timezone.now()
       
        subs = Subscription.objects.filter(user=request.user, is_active=True, expired_at__gt=now)
        if subs.exists():
            sub = subs.first()
            
            sub.expired_at = sub.expired_at + timezone.timedelta(days=plan.duration_days)
            sub.plan = plan
            sub.last_payment_status = "success"
            sub.save()
            PaymentHistory.objects.create(
                user=request.user, subscription=sub, plan_name=plan.name, amount=plan.price,
                status="success", description=f"تمدید {plan.name}"
            )
            send_fcm_notification(request.user, "تمدید موفق اشتراک", f"اشتراک {plan.name} شما تا {sub.expired_at:%Y-%m-%d} تمدید شد.")
            return Response(SubscriptionSerializer(sub).data, status=201)

        expired_at = now + timezone.timedelta(days=plan.duration_days)
        sub = Subscription.objects.create(
            user=request.user, plan=plan, started_at=now, expired_at=expired_at,
            is_active=True, auto_renew=False, last_payment_status="success"
        )
        PaymentHistory.objects.create(
            user=request.user, subscription=sub, plan_name=plan.name, amount=plan.price,
            status="success", description=f"خرید {plan.name}"
        )
        send_fcm_notification(request.user, "خرید موفق اشتراک", f"{plan.name} برای شما فعال شد.")
        return Response(SubscriptionSerializer(sub).data, status=201)

class SubscriptionDeleteView(generics.DestroyAPIView):
    serializer_class = SubscriptionSerializer
    permission_classes = [permissions.IsAuthenticated]
    def get_queryset(self):
        return Subscription.objects.filter(user=self.request.user, is_active=True)
    def perform_destroy(self, instance):
        instance.is_active = False
        instance.save()
        send_fcm_notification(instance.user, "لغو اشتراک", "اشتراک شما غیرفعال شد.")

class PlanListView(generics.ListAPIView):
    serializer_class = PlanSerializer
    queryset = Plan.objects.filter(is_active=True)
    permission_classes = [permissions.AllowAny]

class PaymentHistoryListView(generics.ListAPIView):
    serializer_class = PaymentHistorySerializer
    permission_classes = [permissions.IsAuthenticated]
    def get_queryset(self):
        return PaymentHistory.objects.filter(user=self.request.user).order_by('-pay_time')

class SubscriptionStatsView(views.APIView):
    permission_classes = [permissions.IsAdminUser]
    def get(self, request):
        active = Subscription.objects.filter(is_active=True, expired_at__gt=timezone.now()).count()
        total_buy = PaymentHistory.objects.filter(status='success').count()
        return Response({"active_subscriptions": active, "total_successful_payments": total_buy})
