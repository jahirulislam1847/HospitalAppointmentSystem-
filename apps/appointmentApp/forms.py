from datetime import date, datetime, timedelta
from django import forms
from .models import Appointment
from apps.doctorApp.models import DoctorSchedule

# Map day string/name to Python weekday integer (Monday=0 ... Sunday=6)
DAY_MAP = {
    "monday": 0,
    "tuesday": 1,
    "wednesday": 2,
    "thursday": 3,
    "friday": 4,
    "saturday": 5,
    "sunday": 6,
}


class AppointmentBookingForm(forms.ModelForm):
    target_date = forms.ChoiceField(
        choices=[],
        widget=forms.Select(
            attrs={"class": "w-full rounded-lg border-slate-300 text-sm p-2.5 bg-white"}
        ),
        help_text="Select a date for the next 2 weeks.",
    )
    schedule = forms.ModelChoiceField(
        queryset=DoctorSchedule.objects.none(),
        widget=forms.Select(
            attrs={"class": "w-full rounded-lg border-slate-300 text-sm p-2.5 bg-white"}
        ),
        empty_label="Select recurring schedule",
        help_text="Choose the doctor's weekly shift.",
    )
    appointment_time = forms.ChoiceField(
        choices=[],
        widget=forms.Select(
            attrs={"class": "w-full rounded-lg border-slate-300 text-sm p-2.5 bg-white"}
        ),
        help_text="Select an available time slot.",
    )

    class Meta:
        model = Appointment
        fields = ["schedule", "hospital", "appointment_time"]
        widgets = {
            "hospital": forms.Select(
                attrs={
                    "class": "w-full rounded-lg border-slate-300 text-sm p-2.5 bg-white"
                }
            ),
        }

    def __init__(self, *args, **kwargs):
        doctor = kwargs.pop("doctor", None)
        super().__init__(*args, **kwargs)

        if doctor:
            self.fields["schedule"].queryset = DoctorSchedule.objects.filter(
                doctor=doctor
            )
            self.fields["hospital"].queryset = doctor.hospital.all()

            data = args[0] if args and len(args) > 0 else None
            schedule_id = data.get("schedule") if data else None
            selected_date_str = data.get("target_date") if data else None

            if schedule_id:
                try:
                    selected_schedule = DoctorSchedule.objects.get(
                        pk=schedule_id, doctor=doctor
                    )

                    date_choices = self.generate_upcoming_dates(selected_schedule)
                    self.fields["target_date"].choices = date_choices

                    if selected_date_str:
                        target_dt = datetime.strptime(
                            selected_date_str, "%Y-%m-%d"
                        ).date()
                        slots = self.generate_available_slots(
                            selected_schedule, target_dt
                        )
                        self.fields["appointment_time"].choices = slots
                except (DoctorSchedule.DoesNotExist, ValueError):
                    self.fields["target_date"].choices = []
                    self.fields["appointment_time"].choices = []

    def generate_upcoming_dates(self, schedule):
        """Generates target dates for the next 14 days matching schedule.days."""
        today = date.today()
        upcoming_dates = []

        # Target field on DoctorSchedule is `days`
        raw_day = str(schedule.days).strip().lower()
        target_weekday = DAY_MAP.get(raw_day, 0)

        for i in range(14):
            check_date = today + timedelta(days=i)
            if check_date.weekday() == target_weekday:
                val_str = check_date.strftime("%Y-%m-%d")
                display_str = check_date.strftime("%A, %b %d, %Y")
                upcoming_dates.append((val_str, display_str))

        return upcoming_dates

    def generate_available_slots(self, schedule, target_date):
        """Generates available slots for a schedule on a specific target date."""
        slots = []
        curr_time = datetime.combine(target_date, schedule.start_time)
        end_dt = datetime.combine(target_date, schedule.end_time)
        slot_delta = timedelta(minutes=schedule.slot_duration)

        booked_times = set(
            Appointment.objects.filter(
                doctor=schedule.doctor, appointment_date=target_date
            )
            .exclude(status="cancelled")
            .values_list("appointment_time", flat=True)
        )

        while curr_time + slot_delta <= end_dt:
            t_str = curr_time.time().strftime("%H:%M:%S")
            display_str = curr_time.time().strftime("%I:%M %p")

            if curr_time.time() not in booked_times:
                slots.append((t_str, display_str))

            curr_time += slot_delta

        return slots
