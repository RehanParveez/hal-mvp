from django.core.management.base import BaseCommand
from django.db import connection
from shared.encrypted_fields import compute_cnic_index, _get_fernet

class Command(BaseCommand):
  help = "One-time: encrypts existing plaintext CNIC values and populates cnic_index. Run once, immediately after the encryption migration, before creating any new users."

  def handle(self, *args, **options):
    with connection.cursor() as cursor:
      cursor.execute("SELECT id, cnic FROM accounts_user WHERE cnic IS NOT NULL")
      rows = cursor.fetchall()
    fernet = _get_fernet()
    for user_id, raw_cnic in rows:
      if not raw_cnic:
        continue
      encrypted = fernet.encrypt(raw_cnic.encode()).decode()
      index = compute_cnic_index(raw_cnic)
      with connection.cursor() as cursor:
        cursor.execute("UPDATE accounts_user SET cnic = %s, cnic_index = %s WHERE id = %s", [encrypted, index, user_id])
    self.stdout.write(self.style.SUCCESS(f"Encrypted and indexed {len(rows)} existing CNIC values."))