from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    is_doctor = models.BooleanField(default=False)
    is_patient = models.BooleanField(default=False)
    # Fields for Google Calendar OAuth tokens
    gcal_access_token = models.CharField(max_length=255, blank=True, null=True)
    gcal_refresh_token = models.CharField(max_length=255, blank=True, null=True)

# CORRECTED: Changed models.fields to models.Model
class AvailabilitySlot(models.Model):
    doctor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='slots')
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    is_booked = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.doctor.username} - {self.date} {self.start_time}"

# CORRECTED: Changed models.fields to models.Model
class Booking(models.Model):
    patient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bookings')
    slot = models.OneToOneField(AvailabilitySlot, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)