import json
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os

def send_email(event, context):
    try:
        http_method = (event or {}).get('httpMethod', '').upper()
        if http_method == 'GET':
            return {
                "statusCode": 200,
                "body": json.dumps({
                    "message": "Email endpoint is running. Use POST /dev/send-email to send emails."
                }),
            }

        body = json.loads(event.get('body', '{}'))
        action = body.get('action')
        recipient = body.get('email')
        name = body.get('name', 'User')
        recipient_type = body.get('recipient_type', 'patient')

        subject = ""
        message_body = ""

        if action == "SIGNUP_WELCOME":
            subject = "Welcome to Mini HMS!"
            message_body = f"Hello {name}, welcome to our hospital platform."
        elif action == "BOOKING_CONFIRMATION":
            doctor = body.get('doctor_name', 'Doctor')
            patient = body.get('patient_name', 'Patient')
            time = body.get('time')
            if recipient_type == 'doctor':
                subject = "New Appointment Booked"
                message_body = (
                    f"Hello Dr. {name}, patient {patient} booked a slot at {time}."
                )
            else:
                subject = "Appointment Confirmed"
                message_body = (
                    f"Hello {name}, your appointment with Dr. {doctor} at {time} is confirmed."
                )
        else:
            return {"statusCode": 400, "body": json.dumps({"error": "Invalid action"})}

        # SMTP Setup (Using Gmail as an example)
        sender_email = os.environ.get('SMTP_EMAIL')
        sender_password = os.environ.get('SMTP_PASSWORD')
        if not sender_email or not sender_password:
            return {
                "statusCode": 500,
                "body": json.dumps({
                    "error": "SMTP_EMAIL/SMTP_PASSWORD are not configured"
                }),
            }

        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = recipient
        msg['Subject'] = subject
        msg.attach(MIMEText(message_body, 'plain'))

        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(sender_email, sender_password)
        server.send_message(msg)
        server.quit()

        return {"statusCode": 200, "body": json.dumps({"message": "Email sent successfully!"})}

    except Exception as e:
        return {"statusCode": 500, "body": json.dumps({"error": str(e)})}