import logging
from shared.circuit_breaker import CircuitBreaker
from shared.exceptions import ExternalServiceUnavailable
import requests
from django.conf import settings
from apps.assistant.models import AssistantQuery
from apps.loans.models import LoanApplication
  
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
  def _gather_context(user):
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
    from apps.loans.models import LoanApplication
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
  def _gather_factory_context(user, batch_id): 
    from apps.delivery.models import BatchDelivery
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
    
    def _call_llm():
      if settings.USE_MOCK_AI or not settings.ANTHROPIC_API_KEY:
        if any(k in question.lower() for k in ('simulate error', 'test fallback')):
          raise ExternalServiceUnavailable(service_name = 'AI Assistant')
        return AssistantService._mock_answer(question, context, language_name)
 
      try:
        response = requests.post(
          "https://api.anthropic.com/v1/messages",
          headers={
            "x-api-key": settings.ANTHROPIC_API_KEY, "anthropic-version": "2023-06-01", "content-type": "application/json",
          },
          json={
            "model": "claude-haiku-4-5-20251001", "max_tokens": 400, "system": system_prompt,
             "messages": [{"role": "user", "content": question}],
          },
          timeout=20,
        )
      except requests.exceptions.RequestException as exc:
        raise ExternalServiceUnavailable(service_name = 'AI Assistant') from exc
 
      if response.status_code >= 400:
        raise ExternalServiceUnavailable(service_name = 'AI Assistant')
      return response.json()['content'][0]['text']
 
    try:
      answer = ai_assistant_breaker.call(_call_llm)
      call_status = 'completed'
    except ExternalServiceUnavailable:
      logger.warning(f"Ask Hal unavailable for user {user.id} — breaker open, simulated failure, or upstream failure.")
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