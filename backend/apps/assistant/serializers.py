from rest_framework import serializers
from apps.assistant.models import AssistantQuery

class AskQuestionSerializer(serializers.Serializer):
  question = serializers.CharField(min_length=3, max_length=500)

class AssistantQuerySerializer(serializers.ModelSerializer):
  class Meta:
    model = AssistantQuery
    fields = ['id', 'question', 'answer', 'status', 'created_at']
    read_only_fields = fields