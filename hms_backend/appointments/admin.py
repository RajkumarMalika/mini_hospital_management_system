from django.contrib import admin
from .models import User, AvailabilitySlot, Booking

@admin.register(User)
class CustomUserAdmin(admin.ModelAdmin):
    # This tells Django what columns to show on the user list page
    list_display = ('username', 'email', 'is_doctor', 'is_patient')
    
    # This makes the checkboxes clickable directly from the list page!
    list_editable = ('is_doctor', 'is_patient')

admin.site.register(AvailabilitySlot)
admin.site.register(Booking)