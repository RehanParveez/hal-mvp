from django.db import transaction
from django.utils import timezone
from apps.loans.models import LoanApplication
from shared.exceptions import LoanAlreadyDisbursedError
from apps.escrow.services import EscrowCreationService
from apps.escrow.models import EscrowWallet
from apps.notifications.services import NotificationService
from shared.exceptions import LoanAlreadyDisbursedError, NumberdarVerificationRequiredError, CreditCheckRequiredError

class LoanApplicationService:
  @staticmethod
  def apply_for_loan(farmer_profile, bank_profile, validated_data):
    with transaction.atomic():
      loan = LoanApplication.objects.create(farmer=farmer_profile, bank=bank_profile, status='submitted',
        numberdar_verified_at_application=farmer_profile.user.numberdar_verified, **validated_data)
      return loan

  @staticmethod
  def approve_loan(loan_id, bank_profile, approved_amount, interest_rate_pct):
    with transaction.atomic():
      loan = LoanApplication.objects.select_for_update().get(id=loan_id)
      if loan.bank != bank_profile:
        raise PermissionError("You can only approve loans assigned to your bank.")
      if loan.status != 'submitted':
        raise ValueError(f'only the submitted loans can be approv. Current status: {loan.status}.')
      if approved_amount is None or float(approved_amount) <= 0:
        raise ValueError(f"wrong approved_amount provided: {approved_amount}")
      loan.approved_amount = approved_amount
      loan.interest_rate_pct = interest_rate_pct
      loan.status = 'bank_approved'
      loan.approved_at = timezone.now()
      loan.save()
      
      transaction.on_commit(lambda: NotificationService.notify(loan.farmer.user, 'loan_approved',
       {'approved_amount': approved_amount, 'interest_rate_pct': interest_rate_pct, 'bank_name': bank_profile.institution_name},
       reference_id=loan.id))
      return loan

  @staticmethod
  def reject_loan(loan_id, bank_profile, rejection_reason):
    with transaction.atomic():
      loan = LoanApplication.objects.select_for_update().get(id=loan_id)
      if loan.bank != bank_profile:
        raise PermissionError("You can only reject loans assigned to your bank.")
      if loan.status not in ('submitted', 'bank_approved'):
        raise ValueError(f"cant reject a loan with status '{loan.status}'.")

      loan.status = 'rejected'
      loan.rejection_reason = rejection_reason
      loan.save(update_fields=['status', 'rejection_reason'])
      transaction.on_commit(lambda: NotificationService.notify(
       loan.farmer.user, 'loan_rejected', {'rejection_reason': rejection_reason}, reference_id=loan.id))
      return loan
  
  @staticmethod
  def disburse_loan(loan_id, bank_profile):
    with transaction.atomic():
      loan = LoanApplication.objects.select_for_update().get(id=loan_id)
      if loan.bank != bank_profile:
        raise PermissionError("you can only disburse loans assigned to your bank.")
      if loan.status == 'disbursed':
        raise LoanAlreadyDisbursedError()
      if loan.credit_check_status != 'approved': 
        raise CreditCheckRequiredError()
      if not loan.farmer.user.numberdar_verified:                    
        raise NumberdarVerificationRequiredError()
      if loan.status != 'bank_approved':
        raise ValueError(f"Loan must be bank_approved. Current: {loan.status}.")
      loan.status = 'disbursed'
      loan.disbursed_at = timezone.now()
      loan.save(update_fields=['status', 'disbursed_at'])
      loan.refresh_from_db() 
      escrow = EscrowWallet.objects.filter(loan=loan).first()
      if not escrow:
       escrow = EscrowCreationService.create(loan)
      transaction.on_commit(lambda: NotificationService.notify(loan.farmer.user, 'loan_disbursed', {'escrow_balance': escrow.remaining_balance,
       'insurance_premium': escrow.insurance_premium_deducted},
        reference_id=loan.id))
      return loan, escrow
    
REASON_TEXT = {
  'numberdar_verified':   {'en': 'Verified by your Numberdar.', 'ur': 'آپ کے نمبردار نے تصدیق کر دی ہے۔'},
  'numberdar_unverified': {'en': 'Your local Numberdar has not verified your account yet.', 'ur': 'آپ کے مقامی نمبردار نے ابھی تک آپ کے اکاؤنٹ کی تصدیق نہیں کی۔'},
  'no_loan':              {'en': "You haven't applied for a loan yet.", 'ur': 'آپ نے ابھی تک قرض کے لیے درخواست نہیں دی۔'},
  'bank_approved':        {'en': 'Approved by {bank}.', 'ur': '{bank} نے منظور کر دیا ہے۔'},
  'bank_pending':         {'en': 'Your bank is still reviewing your application.', 'ur': 'آپ کا بینک ابھی آپ کی درخواست کا جائزہ لے رہا ہے۔'},
  'bank_other':           {'en': 'Your application status is: {status}.', 'ur': 'آپ کی درخواست کی حالت: {status}۔'},
  'credit_not_run':       {'en': 'Your credit check has not started yet.', 'ur': 'آپ کا کریڈٹ چیک ابھی شروع نہیں ہوا۔'},
  'credit_pending':       {'en': 'Your credit check is being processed.', 'ur': 'آپ کا کریڈٹ چیک جاری ہے۔'},
  'credit_approved':      {'en': 'Your credit check was approved.', 'ur': 'آپ کا کریڈٹ چیک منظور ہو گیا۔'},
  'credit_rejected':      {'en': 'Your credit check did not pass.', 'ur': 'آپ کا کریڈٹ چیک منظور نہیں ہوا۔'},
  'credit_manual':        {'en': 'Your credit check needs manual review by our team.', 'ur': 'آپ کے کریڈٹ چیک کو ہماری ٹیم کے دستی جائزے کی ضرورت ہے۔'},
  'disbursed':            {'en': 'Your loan has been disbursed into escrow.', 'ur': 'آپ کا قرض ایسکرو میں جاری کر دیا گیا ہے۔'},
  'not_disbursed':        {'en': 'Waiting on the steps above before your bank can disburse.', 'ur': 'بینک کے قرض جاری کرنے سے پہلے اوپر دیے گئے مراحل کا انتظار ہے۔'},
}
LABEL_TEXT = {
  'numberdar_verification': {'en': 'Community Verification', 'ur': 'کمیونٹی تصدیق'},
  'loan_application':       {'en': 'Loan Application', 'ur': 'قرض کی درخواست'},
  'bank_approval':          {'en': 'Bank Approval', 'ur': 'بینک کی منظوری'},
  'credit_check':           {'en': 'Credit Check', 'ur': 'کریڈٹ چیک'},
  'disbursement':           {'en': 'Loan Disbursement', 'ur': 'قرض کا اجراء'},
}

def _t(bank, key, lang, **kwargs):
  text = bank[key].get(lang, bank[key]['en'])
  return text.format(**kwargs) if kwargs else text

class LoanReadinessService:
  @staticmethod
  def get_readiness_checklist(farmer_profile):
    user = farmer_profile.user
    lang = user.preferred_language
    checklist = []

    checklist.append({
      'key': 'numberdar_verification', 'label': _t(LABEL_TEXT, 'numberdar_verification', lang),
      'status': 'complete' if user.numberdar_verified else 'incomplete',
      'reason': _t(REASON_TEXT, 'numberdar_verified' if user.numberdar_verified else 'numberdar_unverified', lang),
      'action_route': '#community-section',
    })

    loan = farmer_profile.loan_applications.select_related('bank').order_by('-created_at').first()
    if not loan:
      checklist.append({
        'key': 'loan_application', 'label': _t(LABEL_TEXT, 'loan_application', lang), 'status': 'incomplete',
          'reason': _t(REASON_TEXT, 'no_loan', lang), 'action_route': '#loan-section'})
      return checklist

    bank_approved = loan.status in ('bank_approved', 'disbursed', 'repaid')
    bank_status = 'complete' if bank_approved else ('incomplete' if loan.status == 'submitted' else 'blocked')
    bank_reason = (_t(REASON_TEXT, 'bank_approved', lang, bank=loan.bank.institution_name) if bank_approved
      else _t(REASON_TEXT, 'bank_pending', lang) if loan.status == 'submitted'
      else _t(REASON_TEXT, 'bank_other', lang, status=loan.status))
    checklist.append({'key': 'bank_approval', 'label': _t(LABEL_TEXT, 'bank_approval', lang),
      'status': bank_status, 'reason': bank_reason, 'action_route': None})

    credit_key = {'not_run': 'credit_not_run', 'pending': 'credit_pending', 'approved': 'credit_approved',
      'rejected': 'credit_rejected', 'manual_review': 'credit_manual'}.get(loan.credit_check_status, 'credit_not_run')
    checklist.append({'key': 'credit_check', 'label': _t(LABEL_TEXT, 'credit_check', lang),
      'status': 'complete' if loan.credit_check_status == 'approved' else 'incomplete',
      'reason': _t(REASON_TEXT, credit_key, lang), 'action_route': '#credit-section'})

    checklist.append({'key': 'disbursement', 'label': _t(LABEL_TEXT, 'disbursement', lang),
      'status': 'complete' if loan.status == 'disbursed' else 'incomplete',
      'reason': _t(REASON_TEXT, 'disbursed' if loan.status == 'disbursed' else 'not_disbursed', lang),
      'action_route': '#escrow-section'})

    return checklist