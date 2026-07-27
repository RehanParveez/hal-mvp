from django.urls import path, include
from rest_framework.routers import DefaultRouter
from apps.assistant.views import AssistantQueryViewSet

router = DefaultRouter()
router.register('queries', AssistantQueryViewSet, basename = 'assistant-queries')

urlpatterns = [path('', include(router.urls))]