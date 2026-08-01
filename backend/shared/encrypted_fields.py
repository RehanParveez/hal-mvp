from cryptography.fernet import Fernet, InvalidToken
import hmac
import hashlib
from django.conf import settings
from django.db import models

def _get_fernet():
  return Fernet(settings.FIELD_ENCRYPTION_KEY.encode())

def compute_cnic_index(raw_cnic):
  return hmac.new(settings.CNIC_INDEX_KEY.encode(), raw_cnic.encode(), hashlib.sha256).hexdigest()

class EncryptedCharField(models.CharField):
  description = "A CharField encrypted at rest with Fernet"

  def __init__(self, *args, **kwargs):
    kwargs['max_length'] = 500
    super().__init__(*args, **kwargs)

  def get_prep_value(self, value):
    if not value:
      return value
    return _get_fernet().encrypt(str(value).encode()).decode()

  def from_db_value(self, value, expression, connection):
    if not value:
      return value
    try:
      return _get_fernet().decrypt(value.encode()).decode()
    except InvalidToken:
      return '[unable to decrypt]'