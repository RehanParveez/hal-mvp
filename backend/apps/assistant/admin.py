from django.contrib import admin
from apps.assistant.models import AssistantQuery

@admin.register(AssistantQuery)
class AssistantQueryAdmin(admin.ModelAdmin):
  list_display = ['id', 'user', 'status', 'created_at']
  list_filter = ['status']
  search_fields = ['user__full_name', 'question']
  readonly_fields = [f.name for f in AssistantQuery._meta.fields]