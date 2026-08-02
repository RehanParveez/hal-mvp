from rest_framework.routers import DefaultRouter
from apps.accounts.views import UserViewSet, AuthViewSet, PasswordResetViewSet
from django.urls import path, include

router = DefaultRouter()
router.register(r'users', UserViewSet, basename = 'user')
router.register(r'', AuthViewSet, basename='auth')
router.register(r'password-reset', PasswordResetViewSet, basename = 'password-reset')

urlpatterns = [
  path('', include(router.urls)),
]