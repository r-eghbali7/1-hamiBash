from celery import shared_task
from kavenegar import KavenegarAPI, APIException, HTTPException
import random
import os

def generate_otp():
    return random.randint(100000, 999999)

@shared_task
def send_otp_to_phone(mobile_number, otp_code):
    try:
        api_key = os.getenv('KAVENEGAR_API_KEY')
        api = KavenegarAPI(api_key)
        params = {
            'receptor': mobile_number,
            'template': 'eghbalicode',
            'token': str(otp_code),
            'type': 'sms'
        }
        api.verify_lookup(params)
    except APIException as e:
        print(f'APIException: {e}')
    except HTTPException as e:
        print(f'HTTPException: {e}')