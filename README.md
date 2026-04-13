
# Mini Hospital Management System (HMS)

A modern, full-stack Hospital Management System designed to handle role-based user authentication, concurrent appointment booking, and asynchronous email notifications. 

This project demonstrates a production-ready architecture by decoupling the core Django backend from an event-driven Serverless email microservice, ensuring high performance and fault tolerance.

## 🚀 Key Features

* **Role-Based Access Control (RBAC):** Custom user models distinguishing between `Doctor` and `Patient` roles, each with dedicated dashboards and permissions.
* **OAuth 2.0 Authentication:** Secure "Sign in with Google" functionality implemented via `django-allauth` and JSON Web Tokens (PyJWT).
* **Concurrency-Safe Booking:** Solves database race conditions using PostgreSQL row-level locking (`select_for_update()`) to guarantee a slot cannot be double-booked by two patients simultaneously.
* **Decoupled Microservice Architecture:** Email confirmations are offloaded to an asynchronous Serverless Framework microservice, preventing the main Django server from hanging during third-party API calls.
* **Responsive UI:** Clean, modern frontend built with Bootstrap 5 and Django Templates.

## 🛠️ Tech Stack

**Core Backend:**
* Python 3.13
* Django 5.0.3
* PostgreSQL (Database)
* `django-allauth` (OAuth & Authentication)

**Microservice (Email):**
* Node.js
* Serverless Framework (`serverless-offline`)

**Frontend:**
* HTML5 / CSS3
* Bootstrap 5
* Django Template Engine

## 🏗️ System Architecture

```text
[ Patient / Doctor ]  ---(HTTP)--->  [ Django Main Server ]  ---> [ PostgreSQL DB ]
                                             |
                                      (Async HTTP POST)
                                             |
                                             v
                               [ Serverless Email Microservice ]
                                             |
                                      (SMTP / Email API)
                                             |
                                             v
                                      [ User's Inbox ]
⚙️ Local Setup & Installation
Prerequisites
Python 3.13+ installed

PostgreSQL installed and running locally

Node.js and npm installed (for the microservice)

Serverless Framework CLI installed (npm install -g serverless)

1. Database Setup
Open pgAdmin or your psql terminal and create a new database:

CREATE DATABASE mini_hms;

2. Backend Setup (Django)
Clone the repository and navigate to the backend directory:

Bash
git clone [https://github.com/RajkumarMalika/mini_hospital_management_system.git](https://github.com/RajkumarMalika/mini_hospital_management_system.git)
cd mini_hospital_management_system/hms_backend
Create a virtual environment and install dependencies:

Bash
python -m venv venv
source venv/bin/activate  # On Windows use: venv\Scripts\activate
pip install -r requirements.txt
Create a .env file in the hms_backend directory:

Code snippet
DB_PASSWORD=your_postgres_password
Run database migrations:

Bash
python manage.py makemigrations
python manage.py migrate
Create a superuser for the admin panel:

Bash
python manage.py createsuperuser
3. Google OAuth Setup
Start the Django server: python manage.py runserver

Log into the admin panel at http://127.0.0.1:8000/admin/

Under Sites, change example.com to 127.0.0.1:8000 (Display name: Mini HMS).

Under Social Applications, add a new Google application using your Client ID and Secret Key from the Google Cloud Console. Move 127.0.0.1:8000 to the chosen sites.

4. Microservice Setup (Email)
Open a second terminal and navigate to the email service folder:

Bash
cd mini_hospital_management_system/email_service
npm install
serverless offline start
The microservice will now listen on http://localhost:3000/dev/send-email.

💻 Usage
To run the full application locally, you must have both servers running simultaneously.

Terminal 1: python manage.py runserver

Terminal 2: serverless offline start

Navigate to http://127.0.0.1:8000/ in your browser.

To test the Doctor Flow, assign the is_doctor permission to a user via the Django admin panel, log in, and create availability slots.

To test the Patient Flow, log in with a standard Google account, view available slots, and book an appointment to trigger the Serverless email confirmation.

🛡️ Handling Database Race Conditions
This project handles the classic "double-booking" problem natively in Django. In appointments/views.py, the booking logic is wrapped in a transaction block:

Python
with transaction.atomic():
    slot = AvailabilitySlot.objects.select_for_update().get(id=slot_id)
    if slot.is_booked:
        # Reject booking...
