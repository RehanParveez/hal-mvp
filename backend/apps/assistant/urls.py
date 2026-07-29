from django.urls import path, include
from rest_framework.routers import DefaultRouter
from apps.assistant.views import AssistantQueryViewSet, SeasonSummaryViewSet

router = DefaultRouter()
router.register('queries', AssistantQueryViewSet, basename = 'assistant-queries')
router.register('season-summary', SeasonSummaryViewSet, basename = 'season-summary')

urlpatterns = [path('', include(router.urls))]