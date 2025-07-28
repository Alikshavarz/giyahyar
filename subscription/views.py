from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from rest_framework.permissions import IsAuthenticated
from datetime import timedelta
from .models import SubscriptionPlan, Subscription, PaymentHistory, Notification
from .serializers import SubscriptionPlanSerializer, PaymentHistorySerializer, NotificationSerializer, SubscriptionSerializer, NotificationSerializer
from .utils import send_notification
from django.utils import timezone

class PlansView(APIView):
    permission_classes = [permissions.AllowAny]
    def get(self, request):
        plans = SubscriptionPlan.objects.filter(is_active=True)
        return Response({"plans": SubscriptionPlanSerializer(plans, many=True).data})

class SubscriptionBuyView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        plan_id = request.data.get('plan_id')
        plan = SubscriptionPlan.objects.filter(id=plan_id, is_active=True).first()
        if not plan:
            return Response({"error": "پلن انتخابی یافت نشد."}, status=404)

        payment = PaymentHistory.objects.create(
            user=request.user, plan=plan, amount=plan.price, is_successful=True, ref_id="SIM12345"
        )
        now = timezone.now()
        last_sub = Subscription.objects.filter(user=request.user, is_active=True, expire_at__gte=now).last()
        if last_sub:
            start_at = last_sub.expire_at
        else:
            start_at = now
        expire_at = start_at + timezone.timedelta(days=plan.duration_days)
        sub = Subscription.objects.create(user=request.user, plan=plan, start_at=start_at, expire_at=expire_at)
        send_notification(request.user, f"اشتراک شما برای {plan.name} تا {expire_at.date()} فعال شد.")
        return Response({
            "message": "پرداخت با موفقیت انجام شد.",
            "subscription": SubscriptionSerializer(sub).data
        })

class PaymentHistoryView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    def get(self, request):
        payments = PaymentHistory.objects.filter(user=request.user).order_by('-created_at')
        return Response({"history": PaymentHistorySerializer(payments, many=True).data})

class NotificationListView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    def get(self, request):
        qs = Notification.objects.filter(user=request.user).order_by('-created_at')
        return Response({"notifications": NotificationSerializer(qs, many=True).data})

from rest_framework.permissions import IsAdminUser

class AdminOverview(APIView):
    permission_classes = [IsAdminUser]
    def get(self, request):
        total_purchases = PaymentHistory.objects.filter(is_successful=True).count()
        total_active_subs = Subscription.objects.filter(is_active=True, expire_at__gte=timezone.now()).count()
        return Response({
            'total_purchases': total_purchases,
            'total_active_subscriptions': total_active_subs,
        })

class AdminPayments(APIView):
    permission_classes = [IsAdminUser]
    def get(self, request):
        qs = PaymentHistory.objects.order_by('-created_at')
        return Response({"all_payments": PaymentHistorySerializer(qs, many=True).data})

class AdminPlans(APIView):
    permission_classes = [IsAdminUser]
    def get(self, request):
        return Response({"plans": SubscriptionPlanSerializer(SubscriptionPlan.objects.all(), many=True).data})

    def post(self, request):
        serializer = SubscriptionPlanSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "پلن جدید اضافه شد.", "plan": serializer.data}, status=201)
        return Response(serializer.errors, status=400)


    def put(self, request, pk=None):
        plan = SubscriptionPlan.objects.filter(pk=pk).last()
        if not plan:
            return Response({"error": "پلان یافت نشد"}, status=404)
        serializer = SubscriptionPlanSerializer(plan, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "پلن ویرایش شد.", "plan": serializer.data})
        return Response(serializer.errors, status=400)

    def delete(self, request, pk=None):
        plan = SubscriptionPlan.objects.filter(pk=pk).last()
        plan.is_active = False
        plan.save()
        return Response({"message": "پلن غیرفعال شد."})
    
    
    
class RememberSubscriptionAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        try:
            subscription = Subscription.objects.get(user=user, is_active=True)
        except Subscription.DoesNotExist:
            return Response({'detail': 'شما اشتراک فعالی ندارید.'}, status=400)

        expire_date = subscription.expire_at
        now = timezone.now()

        if (expire_date - now).days == 3:
            msg = f'اشتراک شما سه روز دیگه ({expire_date.date()}) به پایان می‌رسد. برای تمدید اقدام کنید.'
            create_notification(user, msg)
            return Response({'detail': 'یادآوری ارسال شد.'})
       