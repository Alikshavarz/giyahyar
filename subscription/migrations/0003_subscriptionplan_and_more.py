# Generated by Django 5.2.1 on 2025-07-28 13:51

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('subscription', '0002_subscription_last_payment_status_and_more'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='SubscriptionPlan',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50, unique=True)),
                ('duration_days', models.PositiveIntegerField()),
                ('price', models.PositiveIntegerField()),
                ('is_active', models.BooleanField(default=True)),
                ('description', models.TextField(blank=True, null=True)),
            ],
        ),
        migrations.RemoveField(
            model_name='paymenthistory',
            name='payment_gateway',
        ),
        migrations.RemoveField(
            model_name='paymenthistory',
            name='plan_name',
        ),
        migrations.RemoveField(
            model_name='paymenthistory',
            name='status',
        ),
        migrations.RemoveField(
            model_name='paymenthistory',
            name='subscription',
        ),
        migrations.RemoveField(
            model_name='subscription',
            name='auto_renew',
        ),
        migrations.RemoveField(
            model_name='subscription',
            name='last_payment_status',
        ),
        migrations.AddField(
            model_name='paymenthistory',
            name='is_successful',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='paymenthistory',
            name='ref_id',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.CreateModel(
            name='Notification',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('message', models.TextField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('is_read', models.BooleanField(default=False)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddField(
            model_name='paymenthistory',
            name='plan',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='subscription.subscriptionplan'),
        ),
        migrations.AlterField(
            model_name='subscription',
            name='plan',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='subscription.subscriptionplan'),
        ),
        migrations.DeleteModel(
            name='Plan',
        ),
    ]
