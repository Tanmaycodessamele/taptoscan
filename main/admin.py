from django import forms
from django.contrib import admin, messages

from .models import Card, generate_raw_password, validate_card_id_format


class CardAdminForm(forms.ModelForm):
    # Plain form fields, deliberately named differently from the model's
    # "card_id" field (which is editable=False) so Django admin doesn't
    # reject them. We copy the values onto the instance manually in save_model.
    card_id_input = forms.CharField(
        max_length=32,
        required=False,
        label="Card ID",
        help_text="Leave blank to auto-generate. Or type your own (letters/numbers/dashes).",
    )
    password = forms.CharField(
        max_length=128,
        required=False,
        label="Password",
        widget=forms.TextInput,
        help_text="Leave blank to auto-generate. Or type your own password. (Creating a card only.)",
    )
    new_password = forms.CharField(
        max_length=128,
        required=False,
        label="Set new password",
        widget=forms.TextInput,
        help_text="Only fill this in to CHANGE the password. Leave blank to keep the current one.",
    )

    class Meta:
        model = Card
        fields = ["destination", "is_active"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            self.fields["card_id_input"].initial = self.instance.card_id
            self.fields.pop("password", None)
        else:
            self.fields.pop("new_password", None)

    def clean_card_id_input(self):
        value = self.cleaned_data.get("card_id_input", "").strip().upper()
        if not value:
            return value
        validate_card_id_format(value)
        qs = Card.objects.filter(card_id=value)
        if self.instance and self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise forms.ValidationError("That card ID is already taken.")
        return value


@admin.register(Card)
class CardAdmin(admin.ModelAdmin):
    form = CardAdminForm
    list_display = ("card_id", "is_active", "has_destination", "updated_at", "created_at")
    list_filter = ("is_active",)
    search_fields = ("card_id",)
    readonly_fields = ("created_at", "updated_at")
    actions = ["reset_password_random"]

    @admin.display(boolean=True, description="Has destination")
    def has_destination(self, obj):
        return bool(obj.destination)

    def get_fields(self, request, obj=None):
        if obj is None:
            return ["card_id_input", "password", "destination", "is_active"]
        return ["card_id_input", "new_password", "destination", "is_active", "created_at", "updated_at"]

    def save_model(self, request, obj, form, change):
        typed_card_id = form.cleaned_data.get("card_id_input")

        if not change:
            obj.card_id = typed_card_id or Card.generate_unique_card_id()
            raw_password = form.cleaned_data.get("password") or generate_raw_password()
            obj.set_password(raw_password)
            super().save_model(request, obj, form, change)
            messages.warning(
                request,
                f"Card created. Card ID: {obj.card_id} — Password: {raw_password} "
                "— write this down now; it won't be shown again unless you reset it.",
            )
        else:
            if typed_card_id:
                obj.card_id = typed_card_id
            new_password = form.cleaned_data.get("new_password")
            if new_password:
                obj.set_password(new_password)
            super().save_model(request, obj, form, change)
            if new_password:
                messages.warning(
                    request,
                    f"Password updated for card {obj.card_id}. New password: {new_password}",
                )

    @admin.action(description="Reset password (auto-generate a new random one)")
    def reset_password_random(self, request, queryset):
        results = []
        for card in queryset:
            raw_password = generate_raw_password()
            card.set_password(raw_password)
            card.save(update_fields=["password_hash", "updated_at"])
            results.append(f"{card.card_id}: {raw_password}")
        messages.warning(
            request,
            "New passwords generated (write these down, shown once): " + " | ".join(results),
        )

    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser