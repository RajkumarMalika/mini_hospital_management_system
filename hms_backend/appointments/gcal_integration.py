from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
import datetime

def create_gcal_event(booking):
    """
    Assumes you have logic to retrieve the valid OAuth tokens for both
    the Doctor and the Patient from your User model.
    """
    # Example logic for the Doctor's calendar
    doctor = booking.slot.doctor
    
    # You would typically reconstruct the credentials from the DB here
    # creds = Credentials(token=doctor.gcal_access_token, refresh_token=doctor.gcal_refresh_token, ...)
    
    # For demonstration, assuming 'creds' is valid:
    # service = build('calendar', 'v3', credentials=creds)
    
    start_datetime = datetime.datetime.combine(booking.slot.date, booking.slot.start_time).isoformat()
    end_datetime = datetime.datetime.combine(booking.slot.date, booking.slot.end_time).isoformat()

    event = {
      'summary': f'Appointment with {booking.patient.username}',
      'description': 'Mini HMS Automated Booking',
      'start': {
        'dateTime': start_datetime,
        'timeZone': 'America/Los_Angeles', # Update to your timezone
      },
      'end': {
        'dateTime': end_datetime,
        'timeZone': 'America/Los_Angeles',
      },
    }

    # Execute the API call
    # event = service.events().insert(calendarId='primary', body=event).execute()
    # print('Event created: %s' % (event.get('htmlLink')))
