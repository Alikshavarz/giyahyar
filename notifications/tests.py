from django.test import TestCase
from django.contrib.auth import get_user_model
from .models import FCMDevice

User = get_user_model()

class FCMDeviceModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.device = FCMDevice.objects.create(user=self.user, registration_id='unique_token')

    def test_string_representation(self):
        self.assertEqual(str(self.device), "testuser's FCM Device")

    def test_fcm_device_creation(self):
        self.assertEqual(self.device.user, self.user)
        self.assertEqual(self.device.registration_id, 'unique_token')
        self.assertTrue(self.device.is_active)