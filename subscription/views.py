from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from .models import SubscriptionPlan, PaymentHistory, Subscription, Notification
from .serializers import (
    SubscriptionPlanSerializer, PaymentHistorySerializer, SubscriptionSerializer, NotificationSerializer)
from django.utils import timezone
from django.db.models import Count
from django.contrib.auth import get_user_model
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework import generics, status
from plants import serializers as PlanSerializer


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


class PlansView(APIView):
    permission_classes = [permissions.AllowAny]
    def get(self, request):
        plans = SubscriptionPlan.objects.filter(is_active=True)
        return Response({"plans": SubscriptionPlanSerializer(plans, many=True).data})

class BuySubscriptionView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        plan_id = request.data.get('plan_id')
        plan = SubscriptionPlan.objects.filter(id=plan_id, is_active=True).first()
        if not plan:
            return Response({"error": "پلن مورد نظر یافت نشد."}, status=404)

        now = timezone.now()
        user = request.user
        active_sub = Subscription.objects.filter(user=user, is_active=True, expired_at__gte=now).last()
        if active_sub:
            active_sub.expired_at += timezone.timedelta(days=plan.duration_days)
            active_sub.plan = plan
            active_sub.save()
            sub = active_sub
        else:
            sub = Subscription.objects.create(
                user=user,
                plan=plan,
                start_at=now,
                expired_at=now + timezone.timedelta(days=plan.duration_days),
                is_active=True
            )

        ph = PaymentHistory.objects.create(
            user=user,
            plan=plan,
            amount=plan.price,
            is_successful=True,
            ref_id="TEST-" + str(sub.id)
        )
        Notification.objects.create(
            user=user,
            message=f"اشتراک شما پلن {plan.name} تا تاریخ {sub.expired_at:%Y-%m-%d} فعال شد."
        )
        return Response({
            "message": "خرید و تمدید با موفقیت انجام شد.",
            "subscription": SubscriptionSerializer(sub).data
        })
class MyPaymentsView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        payments = PaymentHistory.objects.filter(user=request.user)
        return Response({"history": PaymentHistorySerializer(payments, many=True).data})

class MyNotificationsView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        qs = Notification.objects.filter(user=request.user).order_by('-created_at')[:50]
        return Response({"notifications": NotificationSerializer(qs, many=True).data})

class SendReminderView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request):
        now = timezone.now()
        subs = Subscription.objects.filter(user=request.user, is_active=True, expired_at__gte=now)
        if not subs.exists():
            return Response({"error": "اشتراک فعالی ندارید!"}, status=400)
        sub = subs.last()
        days_left = (sub.expired_at - now).days
        if 1 < days_left <= 3:
            Notification.objects.create(
                user=request.user,
                message=f"اشتراک شما {days_left} روز دیگر به پایان می‌رسد، فراموش نکنید تمدید کنید."
            )
            return Response({"detail": "یادآوری ارسال شد."})
        return Response({"detail": f"{days_left} روز تا پایان باقی مانده."})


class AdminPlansView(APIView):
    permission_classes = [IsAdminUser]
    def get(self, request):
        plans = SubscriptionPlan.objects.all()
        return Response({"plans": SubscriptionPlanSerializer(plans, many=True).data})

    def post(self, request):
        s = SubscriptionPlanSerializer(data=request.data)
        if s.is_valid():
            plan = s.save()
            return Response({"message": "پلن جدید ثبت شد.", "plan": SubscriptionPlanSerializer(plan).data})
        return Response({"error": s.errors}, status=400)

class AdminPlanDetailView(APIView):
    permission_classes = [IsAdminUser]
    def put(self, request, pk):
        plan = SubscriptionPlan.objects.filter(pk=pk).first()
        if not plan:
            return Response({"error": "پلن یافت نشد"}, status=404)
        s = SubscriptionPlanSerializer(plan, data=request.data, partial=True)
        if s.is_valid():
            plan = s.save()
            return Response({"message": "پلن ویرایش شد.", "plan": SubscriptionPlanSerializer(plan).data})
        return Response({"error": s.errors}, status=400)
    def delete(self, request, pk):
        plan = SubscriptionPlan.objects.filter(pk=pk).first()
        if not plan:
            return Response({"error": "پلن یافت نشد"}, status=404)
        plan.is_active = False
        plan.save()
        return Response({"message": "پلن غیر فعال شد."})

class AdminPaymentsView(APIView):
    permission_classes = [IsAdminUser]
    def get(self, request):
        payments = PaymentHistory.objects.all().order_by('-created_at')
        return Response({"all_payments": PaymentHistorySerializer(payments, many=True).data})

class AdminStatsView(APIView):
    permission_classes = [IsAdminUser]
    def get(self, request):
        n_purchases = PaymentHistory.objects.filter(is_successful=True).count()
        n_active_subs = Subscription.objects.filter(is_active=True, expired_at__gte=timezone.now()).count()
        return Response({
            "فهرست کلی اشتراک ها": n_purchases,
            "اشتراک های فعال": n_active_subs
        })
