from django import forms
from django.core.validators import MaxValueValidator, MinValueValidator

from .models import SOSReport


class SOSReportForm(forms.ModelForm):
    latitude = forms.DecimalField(
        required=False, max_digits=8, decimal_places=6,
        validators=[MinValueValidator(-90), MaxValueValidator(90)],
    )
    longitude = forms.DecimalField(
        required=False, max_digits=9, decimal_places=6,
        validators=[MinValueValidator(-180), MaxValueValidator(180)],
    )

    class Meta:
        model = SOSReport
        fields = ("category", "location", "description", "latitude", "longitude")
        widgets = {"description": forms.Textarea(attrs={"rows": 4})}
        help_texts = {"location": "Enter the campus building, room, or nearest landmark."}

    def clean(self):
        data = super().clean()
        if not ({"latitude", "longitude"} & self.errors.keys()):
            if (data.get("latitude") is None) != (data.get("longitude") is None):
                self.add_error(None, "Enter both coordinates or leave both blank.")
        return data
