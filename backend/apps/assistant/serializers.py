from rest_framework import serializers
from apps.assistant.models import AssistantQuery, SeasonSummary

class AskQuestionSerializer(serializers.Serializer):
  question = serializers.CharField(min_length=3, max_length=500)
  loan_id = serializers.UUIDField(required=False, allow_null=True)
  batch_id = serializers.UUIDField(required=False, allow_null=True)

class AssistantQuerySerializer(serializers.ModelSerializer):
  class Meta:
    model = AssistantQuery
    fields = ['id', 'question', 'answer', 'status', 'created_at']
    read_only_fields = fields
    
class SeasonSummarySerializer(serializers.ModelSerializer):
  class Meta:
    model = SeasonSummary
    fields = ['id', 'narrative', 'status', 'created_at']
    read_only_fields = fields