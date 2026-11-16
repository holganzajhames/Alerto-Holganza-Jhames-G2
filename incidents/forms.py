from django import forms
from django.core.validators import MaxValueValidator, MinValueValidator

from .models import AlertReview, SOSReport


class SOSReportForm(forms.ModelForm):
    latitude = forms.DecimalField(
        required=False, max_digits=8, decimal_places=6,
        validators=[MinValueValidator(-90), MaxValueValidator(90)],
    )
    longitude = forms.DecimalField(
        required=False, max_digits=9, decimal_places=6,
        validators=[MinValueValidator(-180), MaxValueValidator(180)],
    )

    location_accuracy_m = forms.DecimalField(
        required=False, min_value=0, max_digits=8, decimal_places=2,
        label="GPS accuracy in meters",
    )

    class Meta:
        model = SOSReport
        fields = ("category", "location", "description", "latitude", "longitude", "location_accuracy_m")
        widgets = {"description": forms.Textarea(attrs={"rows": 4})}
        help_texts = {"location": "Enter the campus building, room, or nearest landmark."}

    def clean(self):
        data = super().clean()
        if not ({"latitude", "longitude"} & self.errors.keys()):
            latitude_missing = data.get("latitude") is None
            longitude_missing = data.get("longitude") is None
            if latitude_missing != longitude_missing:
                missing_field = "latitude" if latitude_missing else "longitude"
                self.add_error(missing_field, "Enter both coordinates or leave both blank.")
        if data.get("location_accuracy_m") is not None and (
            data.get("latitude") is None or data.get("longitude") is None
        ):
            self.add_error("location_accuracy_m", "GPS accuracy requires both coordinates.")
        return data


class AlertReviewForm(forms.ModelForm):
    class Meta:
        model = AlertReview
        fields = ("decision", "remarks")
        widgets = {"remarks": forms.Textarea(attrs={"rows": 3})}
