import secrets
import bcrypt
from django.db import transaction
from django.utils import timezone
from datetime import timedelta
from apps.accounts.models import User, PasswordResetOTP
from apps.notifications.services import NotificationService

OTP_EXPIRY_MINUTES = 10

class PasswordResetService:
  @staticmethod
  def request_reset(phone):
    try:
      user = User.objects.get(phone=phone)
    except User.DoesNotExist:
      return None

    otp_code = f"{secrets.randbelow(1000000):06d}"
    otp_hash = bcrypt.hashpw(otp_code.encode(), bcrypt.gensalt()).decode()
    with transaction.atomic():
      reset = PasswordResetOTP.objects.create(user=user, otp_hash=otp_hash,
        expires_at=timezone.now() + timedelta(minutes=OTP_EXPIRY_MINUTES))
    NotificationService.notify(user, 'password_reset_otp_sent', {'otp_code': otp_code}, reference_id=reset.id)
    return reset

  @staticmethod
  def verify_reset_otp(reset_id, submitted_otp):
    with transaction.atomic():
      reset = PasswordResetOTP.objects.select_for_update().get(id=reset_id)
      if reset.used:
        raise ValueError("This reset request has already been used.")
      if timezone.now() > reset.expires_at:
        raise ValueError("This code has expired. Please request a new one.")
      if not bcrypt.checkpw(submitted_otp.encode(), reset.otp_hash.encode()):
        raise ValueError("Incorrect code. Please try again.")
      reset.verified = True
      reset.verified_at = timezone.now()
      reset.save(update_fields=['verified', 'verified_at'])
    return reset

  @staticmethod
  def complete_reset(reset_id, new_password):
    with transaction.atomic():
      reset = PasswordResetOTP.objects.select_for_update().select_related('user').get(id=reset_id)
      if not reset.verified:
        raise ValueError("This code has not been verified yet.")
      if reset.used:
        raise ValueError("This reset request has already been used.")
      reset.user.set_password(new_password)
      reset.user.save(update_fields=['password'])
      reset.used = True
      reset.save(update_fields=['used'])
    NotificationService.notify(reset.user, 'password_changed_confirmation', {}, reference_id=reset.id)
    return reset.user