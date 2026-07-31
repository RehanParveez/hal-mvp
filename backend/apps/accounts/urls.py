from rest_framework.routers import DefaultRouter
from apps.accounts.views import UserViewSet, ThrottledTokenObtainPairView
from django.urls import path, include
from rest_framework_simplejwt.views import TokenRefreshView

router = DefaultRouter()
router.register(r'users', UserViewSet, basename = 'user')

urlpatterns = [
  path('', include(router.urls)),
  path('tokenobtainpair/', ThrottledTokenObtainPairView.as_view(), name = 'token_obtain_pair'),
  path('tokenrefresh/', TokenRefreshView.as_view(), name = 'token_refresh'),
]