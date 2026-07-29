from shared.models import BaseModel
from django.db import models

class AssistantQuery(BaseModel):
  STATUS_CHOICES = (
    ('completed', 'Completed'),
    ('failed', 'Failed')
  )
  user = models.ForeignKey('accounts.User', on_delete=models.PROTECT, related_name = 'assistant_queries')
  question = models.TextField()
  answer = models.TextField(blank=True)
  context_snapshot = models.JSONField()
  language = models.CharField(max_length=5, default='ur')
  created_at = models.DateTimeField(auto_now_add=True)
  status = models.CharField(max_length=14, choices=STATUS_CHOICES, default = 'completed', db_index=True)
  role_at_time = models.CharField(max_length=40, blank=True)  
  related_loan = models.ForeignKey('loans.LoanApplication', on_delete=models.SET_NULL, null=True, blank=True,
    related_name = 'assistant_queries')

  class Meta:
    db_table = 'assistant_queries'
    indexes = [models.Index(fields=['user', '-created_at'])]

  def __str__(self):
    return f"AssistantQuery({self.user.full_name}, {self.status})"
  
class SeasonSummary(BaseModel):
  STATUS_CHOICES = (
    ('completed', 'Completed'),
    ('failed', 'Failed')
  )
  settlement_invoice = models.OneToOneField('settlements.SettlementInvoice', on_delete=models.CASCADE, related_name = 'season_summary')
  farmer = models.ForeignKey('accounts.FarmerProfile', on_delete=models.PROTECT, related_name = 'season_summaries')
  narrative = models.TextField(blank=True)
  language = models.CharField(max_length=7, default = 'ur')
  context_snapshot = models.JSONField()
  status = models.CharField(max_length=10, choices=STATUS_CHOICES, default = 'completed')

  class Meta:
    db_table = 'season_summaries'

  def __str__(self):
    return f"SeasonSummary({self.farmer.user.full_name}, {self.status})"