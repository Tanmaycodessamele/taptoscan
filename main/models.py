import secrets
import string

from django.contrib.auth.hashers import check_password, make_password
from django.core.exceptions import ValidationError
from django.core.validators import URLValidator
from django.db import models
from django.db.models import Q


def generate_card_id():
    """8-character random card ID: uppercase letters + digits."""
    alphabet = string.ascii_uppercase + string.digits
    return "".join(secrets.choice(alphabet) for _ in range(8))


def generate_raw_password(length=12):
    alphabet = string.ascii_letters + string.digits
    return "".join(secrets.choice(alphabet) for _ in range(length))

def validate_card_id_format(value):
    """Used when an admin types a CUSTOM card ID instead of auto-generating one."""
    import re
    if not re.fullmatch(r"[A-Z0-9-]{3,32}", value):
        raise ValidationError(
            "Card ID must be 3-32 characters: uppercase letters, numbers, or dashes only."
        )

def validate_http_https(value):
    """Backend validation: destination must be empty or a real http(s) URL."""
    if not value:
        return
    if not (value.startswith("http://") or value.startswith("https://")):
        raise ValidationError("Destination URL must start with http:// or https://")
    URLValidator(schemes=["http", "https"])(value)


class Card(models.Model):
    card_id = models.CharField(max_length=32, unique=True, db_index=True, editable=False)
    password_hash = models.CharField(max_length=128, editable=False)
    destination = models.CharField(
        max_length=500,
        blank=True,
        default="",
        validators=[validate_http_https],
        help_text="Must start with http:// or https://. Leave blank to deactivate.",
    )
    is_active = models.BooleanField(
        default=True,
        help_text="Uncheck to disable this card (e.g. lost card, abuse report).",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.CheckConstraint(
                check=(
                    Q(destination="")
                    | Q(destination__startswith="http://")
                    | Q(destination__startswith="https://")
                ),
                name="destination_http_or_https",
            )
        ]
        ordering = ["-created_at"]

    def __str__(self):
        return self.card_id

    def set_password(self, raw_password):
        self.password_hash = make_password(raw_password)

    def check_password(self, raw_password):
        if not self.password_hash:
            return False
        return check_password(raw_password, self.password_hash)

    @staticmethod
    def generate_unique_card_id():
        while True:
            candidate = generate_card_id()
            if not Card.objects.filter(card_id=candidate).exists():
                return candidate
