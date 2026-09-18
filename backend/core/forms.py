from django import forms 
from core.models import Guest, Business,Booking

class GuestDetailsForm(forms.ModelForm):
    BOOL_CHOICES = [(True, "Yes"), (False, "No")]

    is_business_guest = forms.BooleanField(
        widget=forms.RadioSelect(choices=BOOL_CHOICES),
        required=False,
    )

    class Meta:
        model = Guest
        fields = (
            "first_name",
            "last_name",
            "email",
            "phone",
            "is_business_guest",
        )

class BusinessDetailsForm(forms.ModelForm):
    class Meta:
        model = Business
        fields = ('name',)

class BookingDetailsForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = ('room_type', 'date', 'number_of_night')
        widgets = {'date': forms.DateInput(attrs={'type':'date'})}
