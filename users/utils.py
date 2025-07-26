import random
from django.utils import timezone

def generate_otp():
    return str(random.randint(10000, 99999))

def send_sms(phone_number, code):

    print(f"[OTP SMS] Sent code {code} to {phone_number}")
