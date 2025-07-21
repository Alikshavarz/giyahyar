from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _

class FCMDevice(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='fcm_devices',
        verbose_name=_("User")
    )
    registration_id = models.CharField(
        max_length=255,
        unique=True,
        verbose_name=_("FCM Token")
    )
    created_at = models.DateTimeField(auto_now_add=True)

    is_active = models.BooleanField(
        default=True,
        verbose_name=_("Is Active")
    )

    def __str__(self):
        return f"{self.user.username}'s FCM Device"

    class Meta:
        verbose_name = _("FCM Device")
        verbose_name_plural = _("FCM Devices")