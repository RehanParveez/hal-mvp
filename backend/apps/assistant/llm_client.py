from shared.circuit_breaker import CircuitBreaker
from shared.exceptions import ExternalServiceUnavailable
from django.conf import settings
import requests

ai_assistant_breaker = CircuitBreaker('ai_assistant', failure_threshold=3, cooldown_seconds=120)

def call_claude(system_prompt, user_message, max_tokens=400, model='claude-haiku-4-5-20251001', mock_answer_fn=None):
  """
  Single entry point for every assistant feature's LLM call. Restores the
  mock-mode behavior your original AssistantService.ask() had -- this does
  NOT hit the real, billed Anthropic API when settings.USE_MOCK_AI is on or
  ANTHROPIC_API_KEY is missing.

  mock_answer_fn: optional callable(user_message) -> str, letting each
  feature supply its own fake-response shape (Ask Hal's keyword-based
  canned answers, Season Summary's narrative). If omitted, falls back to
  a generic placeholder -- still zero real API cost either way.
  """
  def _call():
    if settings.USE_MOCK_AI or not settings.ANTHROPIC_API_KEY:
      if any(k in user_message.lower() for k in ('simulate error', 'test fallback')):
        raise ExternalServiceUnavailable(service_name='AI Assistant')
      if mock_answer_fn:
        return mock_answer_fn(user_message)
      return "[Mock] Simulated AI response — USE_MOCK_AI is on, no real API call was made."

    try:
      response = requests.post(
        "https://api.anthropic.com/v1/messages",
        headers={"x-api-key": settings.ANTHROPIC_API_KEY, "anthropic-version": "2023-06-01", "content-type": "application/json"},
        json={"model": model, "max_tokens": max_tokens, "system": system_prompt,
          "messages": [{"role": "user", "content": user_message}]},
        timeout=20,
      )
    except requests.exceptions.RequestException as exc:
      raise ExternalServiceUnavailable(service_name = 'AI Assistant') from exc
    if response.status_code >= 400:
      raise ExternalServiceUnavailable(service_name = 'AI Assistant')
    return response.json()['content'][0]['text']
  return ai_assistant_breaker.call(_call)