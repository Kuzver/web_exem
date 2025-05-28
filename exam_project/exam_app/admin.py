from django.contrib import admin

from django.contrib import admin
from .models import ipexam

@admin.register(ipexam)
class ipexamAdmin(admin.ModelAdmin):
    list_display = ('title', 'exam_date', 'is_public', 'created_at')
    list_filter = ('is_public', 'created_at')
    search_fields = ('title', 'participants__email')
    filter_horizontal = ('participants',)
    date_hierarchy = 'exam_date'
