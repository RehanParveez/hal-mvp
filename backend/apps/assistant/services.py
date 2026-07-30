import logging
from shared.circuit_breaker import CircuitBreaker
from shared.exceptions import ExternalServiceUnavailable
from apps.assistant.models import AssistantQuery
from django.db.models import Sum
from apps.assistant.llm_client import call_claude
from apps.loans.models import LoanApplication
from apps.delivery.models import BatchDelivery
from apps.assistant.models import SeasonSummary  
  
logger = logging.getLogger(__name__)
 
ai_assistant_breaker = CircuitBreaker('ai_assistant', failure_threshold=3, cooldown_seconds=120)
 
SYSTEM_PROMPT_TEMPLATES = {'farmer': """You are "Ask Hal," a read-only explanation assistant inside the Hal agricultural platform.
 
How Hal works, in general (use this to answer general questions):
Hal replaces informal Arthi lending. A farmer is verified by a local Numberdar,
passes a bank-sponsored credit check, and is approved for a loan by a bank. The
loan is disbursed into an escrow account, never as cash. Money unlocks in
phases matching the crop's growth stages, spendable only on inputs allowed in
the current phase, from registered shopkeepers, within official AFO-set price
caps. At harvest, a factory buyer grades the crop and the system automatically
settles: the bank is repaid principal and interest, the landowner (if any)
gets their share, and the farmer receives the remainder as net profit — with
zero fee charged to the farmer anywhere in this process.
 
Rules you must always follow:
- Only use the specific data given to you below about this farmer. Never invent a number, status, or balance not present in it.
- If something isn't in the data provided, say plainly you don't have that information, and suggest who they could ask (their Numberdar, the bank, or Hal support).
- You cannot approve, verify, disburse, or change anything. You only explain. If asked to do something rather than explain something, say plainly that you can only explain, not act.
- Use plain, simple language. Avoid financial jargon where you can.
- Respond in {language_name}.
 
This farmer's current data:
{context_json}
""",

   'bank': """You are "Ask Hal" for a bank manager reviewing loan applications on the Hal platform.
Rules you must always follow:
- Only use the specific loan data given to you below. Never invent a number or status not present in it.
- If no specific loan is referenced, answer only general questions about how Hal's process works.
- You cannot approve, reject, or disburse any loan — you only explain what the platform's own gates and data currently show. If asked to make or override a lending decision, say plainly that's the bank manager's own judgment call, not something you can decide.
- Respond in {language_name}, in a direct, professional tone — no need to simplify financial terminology for this audience.

Loan context: {context_json}""",

  'factory': """You are "Ask Hal" for a factory buyer reviewing deliveries and settlements on the Hal platform.
Rules you must always follow:
- Only use the specific delivery/settlement data given to you below. Never invent a number or status not present in it.
- You must NEVER suggest, recommend, or influence what quality grade to assign to a delivery, or what deduction percentage to apply. If asked anything about grading decisions, say plainly that grading is the factory's own judgment call and you cannot advise on it — this applies even if the question is indirect or hypothetical.
- You can only explain status, contract terms, and figures that already exist in the data below.
- Respond in {language_name}.

Delivery/settlement context: {context_json}""",

}

class AssistantService:
  @staticmethod
  def _gather_farmer_context(user):
    context = {
      'full_name': user.full_name,
      'numberdar_verified': user.numberdar_verified,
      'credit_tier': user.credit_tier,
      'has_loan_application': False,
    }
    farmer_profile = getattr(user, 'farmer_profile', None)
    if not farmer_profile:
      return context
 
    loan = farmer_profile.loan_applications.order_by('-created_at').first()
    if not loan:
      return context
 
    context['has_loan_application'] = True
    context['loan_status'] = loan.status
    context['credit_check_status'] = loan.credit_check_status
    context['requested_amount'] = str(loan.requested_amount)
    context['approved_amount'] = str(loan.approved_amount) if loan.approved_amount else None
 
    escrow = getattr(loan, 'escrow', None)
    if escrow:
      context['escrow_total_funded'] = str(escrow.total_funded)
      context['escrow_remaining_balance'] = str(escrow.remaining_balance)
      active_unlock = escrow.active_unlock
      if active_unlock:
        context['current_phase_name'] = active_unlock.milestone.phase_name
        context['current_phase_allowed_categories'] = active_unlock.milestone.allowed_input_categories
 
    return context
   
  @staticmethod
  def _gather_bank_context(user, loan_id):
    context = {'full_name': user.full_name, 'role': 'bank_manager'}
    if not loan_id:
      context['note'] = 'No specific loan referenced — general questions only.'
      return context

    loan = LoanApplication.objects.select_related('farmer__user', 'credit_check').filter(
      id=loan_id, bank=user.bank_profile).first()
    if not loan:
      context['note'] = 'Referenced loan not found or not assigned to your bank.'
      return context
    context.update({
      'farmer_name': loan.farmer.user.full_name, 
      'farmer_district': loan.farmer.user.district,
      'loan_status': loan.status,
      'requested_amount': str(loan.requested_amount),
      'approved_amount': str(loan.approved_amount) if loan.approved_amount else None,
      'credit_check_status': loan.credit_check_status,
      'numberdar_verified': loan.farmer.user.numberdar_verified,
    })
    if loan.credit_check:
      context['credit_risk_tier'] = loan.credit_check.risk_tier
      context['credit_is_eligible'] = loan.credit_check.is_eligible
    return context
  
  @staticmethod
  def _mock_answer(question, context, language_name):
    q = question.lower()
    if language_name == 'Urdu':
      if any(k in q for k in ('numberdar', 'verif')):
        return ("نمبردار کی تصدیق آپ کی شناخت اور زمین کی معلومات کی تصدیق کرتی ہے، "
                "قرض کی درخواست آگے بڑھنے سے پہلے۔ یہ آپ کا مقامی نمبردار مکمل کرتا ہے۔ [Mock]")
      if 'credit' in q:
        return ("کریڈٹ چیک بینک کو یہ اندازہ لگانے میں مدد دیتا ہے کہ آپ قرض کیسے واپس کریں گے۔ "
                "یہ خودکار ہے اور اس کی کوئی فیس نہیں۔ [Mock]")
      if 'escrow' in q:
        phase = context.get('current_phase_name')
        if phase:
          return (f"آپ کا پیسہ ایسکرو میں ہے، اس وقت '{phase}' مرحلے کے لیے کھلا ہے، "
                  "صرف رجسٹرڈ دکانداروں سے خرچ ہو سکتا ہے۔ [Mock]")
        return "آپ کا ایسکرو بیلنس صرف رجسٹرڈ دکانداروں سے، اجازت شدہ اشیاء پر خرچ ہو سکتا ہے۔ [Mock]"
      return ("ہل آپ کے قرض، ایسکرو، یا تصدیق کی حالت کی وضاحت کر سکتا ہے۔ "
              "میں صرف وضاحت کر سکتا ہوں، منظور یا تبدیل نہیں کر سکتا۔ [Mock]")
    if any(k in q for k in ('numberdar', 'verif')):
      return ("Numberdar verification confirms your identity and land details before your loan "
              "application can move forward. Your local Numberdar completes this step. [Mock]")
    if 'credit' in q:
      return ("A credit check helps the bank assess how you'll repay the loan. It's automatic "
              "and there's no fee charged to you for it. [Mock]")
    if 'escrow' in q:
      phase = context.get('current_phase_name')
      if phase:
        return (f"Your money is held in escrow and is currently unlocked for the '{phase}' phase — "
                f"spendable only with registered shopkeepers on items allowed in this phase. [Mock]")
      return "Your escrow balance can only be spent with registered shopkeepers, on approved items. [Mock]"
    return ("Hal can explain your loan, escrow, or verification status. "
            "I can only explain — I can't approve or change anything. [Mock]")

  @staticmethod
  def _gather_factory_context(user, batch_id): 
    context = {'full_name': user.full_name, 'role': 'factory_buyer'}
    if not batch_id:
      context['note'] = 'No specific delivery referenced — general questions only.'
      return context
    batch = BatchDelivery.objects.select_related('allocation__contract').filter(
      id=batch_id, allocation__contract__factory=user.factory_profile).first()
    if not batch:
      context['note'] = 'Referenced delivery not found or not assigned to your contracts.'
      return context
    context.update({
      'batch_kg': str(batch.batch_kg), 'batch_status': batch.status,
      'expected_payout': str(batch.expected_payout),
      'actual_payout': str(batch.actual_payout) if batch.actual_payout else None,
      'grade_received': batch.grade_received or None,
      'payment_defer_days': batch.allocation.contract.payment_defer_days,
    })
    invoice = getattr(batch, 'invoice', None)
    if invoice:
      context['settlement_status'] = invoice.status
    return context

  @staticmethod
  def _gather_context(user, loan_id=None, batch_id=None):
    if user.role in ('smallholder', 'tenant'):
      return AssistantService._gather_farmer_context(user)
    if user.role == 'bank':
      return AssistantService._gather_bank_context(user, loan_id)
    if user.role == 'factory':
      return AssistantService._gather_factory_context(user, batch_id)
    return {'full_name': user.full_name, 'role': user.role}
  
  @staticmethod
  def _mock_answer(question, context, language_name):
    q = question.lower()
 
    if language_name == 'Urdu':
      if any(k in q for k in ('numberdar', 'verif')):
        return ("نمبردار کی تصدیق آپ کی شناخت اور زمین کی معلومات کی تصدیق کرتی ہے، "
                "قرض کی درخواست آگے بڑھنے سے پہلے۔ یہ آپ کا مقامی نمبردار مکمل کرتا ہے۔ [Mock]")
      if 'credit' in q:
        return ("کریڈٹ چیک بینک کو یہ اندازہ لگانے میں مدد دیتا ہے کہ آپ قرض کیسے واپس کریں گے۔ "
                "یہ خودکار ہے اور اس کی کوئی فیس نہیں۔ [Mock]")
      if 'escrow' in q:
        phase = context.get('current_phase_name')
        if phase:
          return (f"آپ کا پیسہ ایسکرو میں ہے، اس وقت '{phase}' مرحلے کے لیے کھلا ہے، "
                  "صرف رجسٹرڈ دکانداروں سے خرچ ہو سکتا ہے۔ [Mock]")
        return "آپ کا ایسکرو بیلنس صرف رجسٹرڈ دکانداروں سے، اجازت شدہ اشیاء پر خرچ ہو سکتا ہے۔ [Mock]"
      return ("ہل آپ کے قرض، ایسکرو، یا تصدیق کی حالت کی وضاحت کر سکتا ہے۔ "
              "میں صرف وضاحت کر سکتا ہوں، منظور یا تبدیل نہیں کر سکتا۔ [Mock]")
 
    if any(k in q for k in ('numberdar', 'verif')):
      return ("Numberdar verification confirms your identity and land details before your loan "
              "application can move forward. Your local Numberdar completes this step. [Mock]")
    if 'credit' in q:
      return ("A credit check helps the bank assess how you'll repay the loan. It's automatic "
              "and there's no fee charged to you for it. [Mock]")
    if 'escrow' in q:
      phase = context.get('current_phase_name')
      if phase:
        return (f"Your money is held in escrow and is currently unlocked for the '{phase}' phase — "
                f"spendable only with registered shopkeepers on items allowed in this phase. [Mock]")
      return "Your escrow balance can only be spent with registered shopkeepers, on approved items. [Mock]"
    return ("Hal can explain your loan, escrow, or verification status. "
            "I can only explain — I can't approve or change anything. [Mock]")
 
  @staticmethod
  def ask(user, question, loan_id=None, batch_id=None):
    context = AssistantService._gather_context(user, loan_id=loan_id, batch_id=batch_id)
    language_name = 'Urdu' if user.preferred_language == 'ur' else 'English'
    template_key = 'bank' if user.role == 'bank' else 'factory' if user.role == 'factory' else 'farmer'
    system_prompt = SYSTEM_PROMPT_TEMPLATES[template_key].format(language_name=language_name, context_json=context)
  
    mock_fn = lambda q: AssistantService._mock_answer(q, context, language_name) 

    try:
      answer = call_claude(system_prompt, question, mock_answer_fn=mock_fn)  
      call_status = 'completed'
    except ExternalServiceUnavailable:
      logger.warning(f"Ask Hal unavailable for user {user.id} — breaker open, mock-simulated failure, or upstream failure.")
      answer = ("I'm not able to answer right now — please try again in a few minutes, "
                 "or check with your Numberdar or bank manager.") if language_name == 'English' else \
                ("میں ابھی جواب نہیں دے سکتا — چند منٹ بعد دوبارہ کوشش کریں، "
                 "یا اپنے نمبردار یا بینک منیجر سے رابطہ کریں۔")
      call_status = 'failed'

    related_loan = None
    if user.role == 'bank' and loan_id:
      related_loan = LoanApplication.objects.filter(id=loan_id, bank=user.bank_profile).first()

    return AssistantQuery.objects.create(user=user, question=question, answer=answer, language=user.preferred_language,
      context_snapshot=context, status=call_status, role_at_time=user.role, related_loan=related_loan)
    
class SeasonSummaryService:
  @staticmethod
  def _gather_journey_context(invoice):
    loan = invoice.loan
    batch = invoice.batch
    context = {
      'crop_name': loan.crop.name, 'acres_applied_for': str(loan.acres_applied_for),
      'requested_amount': str(loan.requested_amount), 'approved_amount': str(loan.approved_amount),
      'credit_risk_tier': loan.credit_check.risk_tier if loan.credit_check else None,
      'batch_kg': str(batch.batch_kg), 'grade_received': batch.grade_received,
      'grade_deduction_pct': str(batch.grade_deduction_pct),
      'gross_payout': str(invoice.gross_payout),
      'principal_repaid': str(invoice.proportional_principal_deduction),
      'interest_paid': str(invoice.bank_interest_deduction),
      'farmer_net_profit': str(invoice.farmer_net_profit),
      'theka_or_batai_paid': str(invoice.theka_payment or invoice.batai_landowner_share or 0),
      'insurance_triggered': invoice.insurance_claim_triggered,
    }
    if hasattr(loan, 'escrow'):
      spend_by_category = (loan.escrow.transactions.filter(txn_type='input')
        .values('input_category').annotate(total=Sum('amount')))
      context['input_spend_by_category'] = {row['input_category']: str(row['total']) for row in spend_by_category}
    return context

  @staticmethod
  def _mock_narrative(context, language_name):
    if language_name == 'Urdu':
      return (
        f"آپ نے {context.get('acres_applied_for')} ایکڑ پر {context.get('crop_name')} کے لیے "
        f"PKR {context.get('approved_amount')} کا قرض لیا۔ فصل {context.get('batch_kg')} کلوگرام کٹی، "
        f"گریڈ {context.get('grade_received')}۔ کل ادائیگی PKR {context.get('gross_payout')} تھی، "
        f"جس میں سے PKR {context.get('principal_repaid')} اصل رقم اور PKR {context.get('interest_paid')} سود کاٹا گیا۔ "
        f"آپ کا خالص منافع PKR {context.get('farmer_net_profit')} رہا۔ [Mock]"
      )
    return (
      f"You took a loan of PKR {context.get('approved_amount')} for {context.get('acres_applied_for')} acres of "
      f"{context.get('crop_name')}. Your harvest came in at {context.get('batch_kg')} kg, graded "
      f"{context.get('grade_received')}. Total payout was PKR {context.get('gross_payout')}, with "
      f"PKR {context.get('principal_repaid')} going to loan principal and PKR {context.get('interest_paid')} to interest. "
      f"You ended the season with a net profit of PKR {context.get('farmer_net_profit')}. [Mock]"
    )

  @staticmethod
  def generate(farmer_profile, invoice):
    if invoice.loan.farmer_id != farmer_profile.id:
      raise PermissionError("this settlement does not belong to you.")

    existing = SeasonSummary.objects.filter(settlement_invoice=invoice).first()
    if existing:
      return existing

    context = SeasonSummaryService._gather_journey_context(invoice)
    user = farmer_profile.user
    language_name = 'Urdu' if user.preferred_language == 'ur' else 'English'
    system_prompt = (
      "Write a short, warm, plain-language season summary for a farmer on the Hal "
      "platform, using ONLY the real numbers below — never invent a figure. Structure "
      "it as: what the loan was for, what was spent and on what, how the harvest "
      f"went, and what the farmer ended up with as net profit. 4-6 short sentences. "
      f"Respond in {language_name}.\n\nData: {context}"
    )

    mock_fn = lambda _msg: SeasonSummaryService._mock_narrative(context, language_name)

    try:
      narrative = call_claude(system_prompt, "Write my season summary.", max_tokens=300, mock_answer_fn=mock_fn) 
      call_status = 'completed'
    except ExternalServiceUnavailable:
      narrative = ("Your season summary isn't available right now — please try again shortly."
        if language_name == 'English' else "آپ کے سیزن کا خلاصہ ابھی دستیاب نہیں ہے — براہ کرم تھوڑی دیر بعد کوشش کریں۔")
      call_status = 'failed'

    return SeasonSummary.objects.create(
      settlement_invoice=invoice, farmer=farmer_profile, narrative=narrative,
      language=user.preferred_language, context_snapshot=context, status=call_status)