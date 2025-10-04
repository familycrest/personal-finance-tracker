from secrets import token_hex

from . import models

def create_auth_code(user: models.UserAccount) -> str:
    code = token_hex(3).upper()
    
    models.AuthCode.objects.update_or_create(
        user=user,
        defaults={
            "user": user,
            "code": code
        }
    )

    return code

def send_verif_email(email: str, code: str):
    print(f"Email integration is incomplete, here's the code to paste in: {code}")
    
def verify_email_code(email: str, test_code: str):
    pass

