from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.http import HttpResponse
from django.contrib import messages
from django.views.decorators.http import require_POST
from datetime import date as dt_date, time as dt_time
import requests
from .models import AvailabilitySlot, Booking

# 1. The Home Router
@login_required
def home(request):
    """Routes the user to the correct dashboard based on their role."""
    if request.user.is_doctor:
        return redirect('doctor_dashboard')
    elif request.user.is_patient:
        return redirect('patient_dashboard')
    else:
        # Default to patient if they just signed up via Google
        request.user.is_patient = True
        request.user.save()
        return redirect('patient_dashboard')

# 2. Doctor Dashboard
@login_required
def doctor_dashboard(request):
    slots = AvailabilitySlot.objects.filter(doctor=request.user).order_by('date', 'start_time')
    return render(request, 'appointments/doctor_dashboard.html', {'slots': slots})

# 3. Patient Dashboard
@login_required
def patient_dashboard(request):
    available_slots = AvailabilitySlot.objects.filter(is_booked=False).order_by('date', 'start_time')
    my_bookings = Booking.objects.filter(patient=request.user).order_by('slot__date', 'slot__start_time')
    
    context = {
        'available_slots': available_slots,
        'my_bookings': my_bookings
    }
    return render(request, 'appointments/patient_dashboard.html', context)

# 4. Add Slot Logic (The part that was missing!)
@login_required
@require_POST
def add_slot(request):
    if not request.user.is_doctor:
        return HttpResponse("Unauthorized. Only doctors can add slots.", status=401)

    slot_date_raw = request.POST.get('date', '').strip()
    start_time_raw = request.POST.get('start_time', '').strip()
    end_time_raw = request.POST.get('end_time', '').strip()

    try:
        slot_date = dt_date.fromisoformat(slot_date_raw)
        start_time = dt_time.fromisoformat(start_time_raw)
        end_time = dt_time.fromisoformat(end_time_raw)
    except ValueError:
        messages.error(request, 'Please provide a valid date and time values.')
        return redirect('doctor_dashboard')

    if slot_date < dt_date.today():
        messages.error(request, 'You cannot add availability in the past.')
        return redirect('doctor_dashboard')

    if end_time <= start_time:
        messages.error(request, 'End time must be later than start time.')
        return redirect('doctor_dashboard')

    AvailabilitySlot.objects.create(
        doctor=request.user,
        date=slot_date,
        start_time=start_time,
        end_time=end_time
    )
    messages.success(request, 'Availability slot added successfully!')
    return redirect('doctor_dashboard')

# 5. Book Appointment Logic (With Race Condition Protection)
@login_required
@require_POST
def book_appointment(request, slot_id):
    if not request.user.is_patient:
        return HttpResponse("Unauthorized. Only patients can book slots.", status=401)

    try:
        with transaction.atomic():
            # Lock the row to prevent double-booking
            slot = AvailabilitySlot.objects.select_for_update().get(id=slot_id)

            if slot.is_booked:
                messages.error(request, "Sorry, this slot was just booked by someone else.")
                return redirect('patient_dashboard')

            # Mark as booked
            slot.is_booked = True
            slot.save()

            # Create Booking
            Booking.objects.create(patient=request.user, slot=slot)

            # Trigger Serverless Email Function for both patient and doctor.
            booking_time = f"{slot.date} {slot.start_time}"
            patient_payload = {
                "action": "BOOKING_CONFIRMATION",
                "email": request.user.email,
                "recipient_type": "patient",
                "name": request.user.username or request.user.email,
                "doctor_name": slot.doctor.username or slot.doctor.email,
                "time": booking_time,
            }
            doctor_payload = {
                "action": "BOOKING_CONFIRMATION",
                "email": slot.doctor.email,
                "recipient_type": "doctor",
                "name": slot.doctor.username or slot.doctor.email,
                "patient_name": request.user.username or request.user.email,
                "time": booking_time,
            }

            for payload in (patient_payload, doctor_payload):
                if not payload.get("email"):
                    continue
                try:
                    response = requests.post(
                        'http://localhost:3000/dev/send-email',
                        json=payload,
                        timeout=5,
                    )
                    if response.status_code >= 400:
                        print(
                            f"Email failed for {payload.get('recipient_type')} "
                            f"({payload.get('email')}): {response.status_code} {response.text}"
                        )
                except Exception as e:
                    print(
                        f"Serverless email failed for {payload.get('recipient_type')} "
                        f"({payload.get('email')}), but booking succeeded.",
                        e,
                    )

            messages.success(request, "Booking Successful!")
            return redirect('patient_dashboard')

    except AvailabilitySlot.DoesNotExist:
        return HttpResponse("Slot not found.", status=404)