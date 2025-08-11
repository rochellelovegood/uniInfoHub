from django.contrib import admin
from .models import UserProfile,Scholarship,Company,Testimonial
# Register your models here.
admin.site.register(UserProfile)
admin.site.register(Scholarship)

@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ('name', 'website', 'display_order')
    list_editable = ('display_order',)
    search_fields = ('name',)
    ordering = ('display_order',)

@admin.register(Testimonial)
class TestimonialAdmin(admin.ModelAdmin):
    list_display = ('student_name', 'company', 'role', 'display_order')
    list_editable = ('display_order',)
    search_fields = ('student_name', 'company')
    ordering = ('display_order',)