from django import forms
from django.utils.translation import gettext_lazy as _


class RoleSignupForm(forms.Form):
    ROLE_DOCTOR = "doctor"
    ROLE_PATIENT = "patient"

    role = forms.ChoiceField(
        label=_("Sign up as"),
        choices=(
            (ROLE_DOCTOR, _("Doctor")),
            (ROLE_PATIENT, _("Patient")),
        ),
        widget=forms.RadioSelect,
        initial=ROLE_PATIENT,
    )

    def signup(self, request, user):
        selected_role = self.cleaned_data.get("role", self.ROLE_PATIENT)
        user.is_doctor = selected_role == self.ROLE_DOCTOR
        user.is_patient = selected_role == self.ROLE_PATIENT
        user.save(update_fields=["is_doctor", "is_patient"])
