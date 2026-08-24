from django.contrib import admin

from .models import Hospital


@admin.register(Hospital)
class HospitalAdmin(admin.ModelAdmin):
    list_display = ('id','name', 'email', 'contact', 'created_by', 'created_at')
    search_fields = ('name', 'email', 'contact')
    list_filter = ('created_at',)
    readonly_fields = ('created_at',)
