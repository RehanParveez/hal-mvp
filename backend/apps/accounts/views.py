from django.contrib.auth import get_user_model
from rest_framework import viewsets, status, permissions
from apps.accounts.serializers import UserRegistrationSerializer, UserSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.parsers import MultiPartParser
from apps.accounts.models import CorporateVerificationDocument, ShopkeeperProfile
from apps.accounts.serializers import DocumentUploadSerializer
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.throttling import ScopedRateThrottle
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer, TokenRefreshSerializer
from rest_framework_simplejwt.exceptions import TokenError, InvalidToken
from django.conf import settings
from shared.constants import PUNJAB_DIVISIONS

User = get_user_model()

REFRESH_COOKIE_NAME = 'hal_refresh_token'
REFRESH_COOKIE_MAX_AGE = 60 * 60 * 24

def _set_refresh_cookie(response, token):
  response.set_cookie(REFRESH_COOKIE_NAME, token, max_age=REFRESH_COOKIE_MAX_AGE,
    httponly=True, secure=not settings.DEBUG, samesite='Strict')

class UserViewSet(viewsets.ModelViewSet):
  serializer_class = UserSerializer 

  def get_permissions(self):
    if self.action in ('create', 'reference_data'):
      return [permissions.AllowAny()]
    return [permissions.IsAuthenticated()]

  def get_serializer_class(self):
    if self.action == 'create':
      return UserRegistrationSerializer
    return UserSerializer

  def get_queryset(self):
    user = self.request.user
    if not user.is_authenticated:
      return User.objects.none()
    if getattr(user, 'role', None) == 'admin':
      return User.objects.all()
    if getattr(user, 'role', None) == 'bank':
      return User.objects.filter(province=user.province)
    if getattr(user, 'role', None) == 'factory':
      return User.objects.filter(role__in=['smallholder', 'tenant', 'landowner'])
    return User.objects.filter(id=user.id)

  def create(self, request, *args, **kwargs):
    serializer = self.get_serializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    user = serializer.save()
    refresh = RefreshToken.for_user(user)
    return Response({'access': str(refresh.access_token), 'refresh': str(refresh), 
      'user': UserSerializer(user).data}, status=status.HTTP_201_CREATED)

  @action(detail=False, methods=['get', 'patch'])
  def profile(self, request):
    if request.method == 'PATCH':
      serializer = self.get_serializer(request.user, data=request.data, partial=True)
      serializer.is_valid(raise_exception=True)
      serializer.save()
      return Response(serializer.data, status=status.HTTP_200_OK)
    serializer = self.get_serializer(request.user)
    return Response(serializer.data, status=status.HTTP_200_OK)
  
  @action(detail=False, methods=['get'])
  def banks(self, request):
    from apps.accounts.models import BankProfile
    banks = BankProfile.objects.select_related('user').all()
    data = [{'id': str(b.id), 'name': b.institution_name, 'branch_code': b.branch_code} for b in banks]
    return Response(data)

  @action(detail=False, methods=['get'])
  def shopkeepers(self, request):
    shopkeepers = ShopkeeperProfile.objects.select_related('user').all()
    data = [{'id': str(s.user.id), 'name': s.shop_name, 'phone': s.user.phone} for s in shopkeepers]
    return Response(data)
  
  @action(detail=False, methods=['post'], parser_classes=[MultiPartParser])
  def upload_verification_document(self, request):
    serializer = DocumentUploadSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    doc, _ = CorporateVerificationDocument.objects.update_or_create(user=request.user, document_type=serializer.validated_data['document_type'],
      defaults={'file': serializer.validated_data['file']})
    return Response({'message': 'Document uploaded.', 'document_type': doc.document_type}, status=status.HTTP_201_CREATED)
  
class ThrottledTokenObtainPairView(TokenObtainPairView):
  throttle_classes = [ScopedRateThrottle]
  throttle_scope = 'login'
  
REFRESH_COOKIE_NAME = 'hal_refresh_token'
REFRESH_COOKIE_MAX_AGE = 60 * 60 * 24

def _set_refresh_cookie(response, token):
  response.set_cookie(REFRESH_COOKIE_NAME, token, max_age=REFRESH_COOKIE_MAX_AGE,
    httponly=True, secure=not settings.DEBUG, samesite='Strict')

class AuthViewSet(viewsets.ViewSet):
  def get_permissions(self):
    if self.action == 'logout':
      return [IsAuthenticated()]
    return [AllowAny()]

  def get_throttles(self):
    if self.action == 'token_obtain_pair':
      self.throttle_scope = 'login'
      return [ScopedRateThrottle()]
    return super().get_throttles()

  @action(detail=False, methods=['get'], url_path='reference-data')
  def reference_data(self, request):
    return Response({'province': 'Punjab', 'district_divisions': PUNJAB_DIVISIONS})

  @action(detail=False, methods=['post'], url_path='tokenobtainpair')
  def token_obtain_pair(self, request):
    serializer = TokenObtainPairSerializer(data=request.data)
    try:
      serializer.is_valid(raise_exception=True)
    except TokenError as e:
      raise InvalidToken(e.args[0])
    data = serializer.validated_data
    refresh_token = data.pop('refresh')
    response = Response(data, status=status.HTTP_200_OK)
    _set_refresh_cookie(response, refresh_token)
    return response

  @action(detail=False, methods=['post'], url_path='tokenrefresh')
  def token_refresh(self, request):
    refresh_token = request.COOKIES.get(REFRESH_COOKIE_NAME)
    if not refresh_token:
      return Response({'error': 'No refresh token found.'}, status=status.HTTP_401_UNAUTHORIZED)
    serializer = TokenRefreshSerializer(data={'refresh': refresh_token})
    try:
      serializer.is_valid(raise_exception=True)
    except TokenError as e:
      raise InvalidToken(e.args[0])
    data = serializer.validated_data
    response = Response({'access': data['access']}, status=status.HTTP_200_OK)
    if 'refresh' in data: 
      _set_refresh_cookie(response, data['refresh'])
    return response

  @action(detail=False, methods=['post'], url_path='logout')
  def logout(self, request):
    response = Response({'message': 'Logged out.'})
    response.delete_cookie(REFRESH_COOKIE_NAME)
    return response