from rest_framework import viewsets, status
from apps.assistant.serializers import AssistantQuerySerializer, AskQuestionSerializer, SeasonSummarySerializer
from shared.permissions import FarmerPermission, BankManagerPerm, FactoryPerm
from rest_framework.throttling import ScopedRateThrottle
from apps.assistant.models import AssistantQuery
from rest_framework.decorators import action
from apps.assistant.services import AssistantService, SeasonSummaryService
from rest_framework.response import Response
from apps.settlements.models import SettlementInvoice
from shared.pagination import TimelineCursorPagination

class AssistantQueryViewSet(viewsets.ReadOnlyModelViewSet):
  serializer_class = AssistantQuerySerializer
  pagination_class = TimelineCursorPagination

  def get_permissions(self):  
    return [(FarmerPermission | BankManagerPerm | FactoryPerm)()]

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
    query = AssistantService.ask(user=request.user, question=serializer.validated_data['question'],
      loan_id=serializer.validated_data.get('loan_id'), batch_id=serializer.validated_data.get('batch_id'))
    return Response(AssistantQuerySerializer(query).data, status=status.HTTP_201_CREATED)
  
class SeasonSummaryViewSet(viewsets.ViewSet):
  permission_classes = [FarmerPermission]

  def get_throttles(self):
    self.throttle_scope = 'ai_assistant'
    return [ScopedRateThrottle()]

  def retrieve(self, request, pk=None):
    invoice = SettlementInvoice.objects.select_related(
      'loan__crop', 'loan__credit_check', 'batch', 'loan__escrow'
    ).filter(id=pk, loan__farmer=request.user.farmer_profile).first()
    if not invoice:
      return Response({'error': 'Settlement not found.'}, status=status.HTTP_404_NOT_FOUND)
    try:
      summary = SeasonSummaryService.generate(request.user.farmer_profile, invoice)
    except PermissionError as e:
      return Response({'error': str(e)}, status=status.HTTP_403_FORBIDDEN)
    return Response(SeasonSummarySerializer(summary).data)