from rest_framework import viewsets, status
from apps.assistant.serializers import AssistantQuerySerializer, AskQuestionSerializer
from shared.permissions import FarmerPermission
from rest_framework.throttling import ScopedRateThrottle
from apps.assistant.models import AssistantQuery
from rest_framework.decorators import action
from apps.assistant.services import AssistantService
from rest_framework.response import Response

class AssistantQueryViewSet(viewsets.ReadOnlyModelViewSet):
  serializer_class = AssistantQuerySerializer
  permission_classes = [FarmerPermission]

  def get_throttles(self):
    if self.action == 'ask':
      self.throttle_scope = 'ai_assistant'
      return [ScopedRateThrottle()]
    return super().get_throttles()

  def get_queryset(self):
    return AssistantQuery.objects.filter(user=self.request.user).order_by('-created_at')

  @action(detail=False, methods=['post'])
  def ask(self, request):
    serializer = AskQuestionSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    query = AssistantService.ask(user=request.user, question=serializer.validated_data['question'])
    return Response(AssistantQuerySerializer(query).data, status=status.HTTP_201_CREATED)