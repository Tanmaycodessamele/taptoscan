from django import forms

from .models import validate_http_https


class ManageCardForm(forms.Form):
    card_id = forms.CharField(
        max_length=32,
        label="Card ID",
        widget=forms.TextInput(attrs={"autocomplete": "off", "autocapitalize": "characters"}),
    )
    password = forms.CharField(
        max_length=128,
        label="Card Password",
        widget=forms.PasswordInput(attrs={"autocomplete": "off"}),
    )
    destination = forms.CharField(
        max_length=500,
        label="Destination URL",
        validators=[validate_http_https],
        widget=forms.URLInput(attrs={"placeholder": "https://example.com"}),
    )

    def clean_card_id(self):
        return self.cleaned_data["card_id"].strip().upper()

    def clean_destination(self):
        dest = self.cleaned_data["destination"].strip()
        if not (dest.startswith("http://") or dest.startswith("https://")):
            raise forms.ValidationError("Destination must start with http:// or https://")
        return dest
