from django.contrib import admin
from gsb.models import Key, List, Record

class ListAdmin(admin.ModelAdmin):
    list_display = ['name', '_is_active', 'major', 'minor', 'errors', 'update_time', 'next_update']
    # list_filter = ['created_on', 'user']
    # date_hierarchy = 'created_on'
    # ordering = ['-created_on', 'user']
    # search_fields = ['payment_no', 'created_on']

admin.site.register(List, ListAdmin)

