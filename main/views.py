from django.core.exceptions import ValidationError
from django.http import HttpResponse
from django.shortcuts import redirect, render

from .forms import ManageCardForm
from .models import Card

# Reserved path segments that must never be treated as a card ID lookup.
RESERVED_SLUGS = {"admin", "manage", "thank-you", "privacy", "robots.txt", "favicon.ico"}


def manage_view(request):
    """
    The one page: card ID + password + destination.
    Correct ID + password updates the destination immediately.
    """
    error = None
    if request.method == "POST":
        form = ManageCardForm(request.POST)
        if form.is_valid():
            card_id = form.cleaned_data["card_id"]
            password = form.cleaned_data["password"]
            destination = form.cleaned_data["destination"]

            card = Card.objects.filter(card_id=card_id, is_active=True).first()

            # Generic error either way — never reveal whether the card ID exists.
            if card and card.check_password(password):
                card.destination = destination
                try:
                    card.full_clean()
                except ValidationError:
                    error = "That destination isn't a valid http:// or https:// link."
                else:
                    card.save(update_fields=["destination", "updated_at"])
                    return redirect("thank_you")
            else:
                error = "Invalid card ID or password."
    else:
        form = ManageCardForm()

    return render(request, "main/manage.html", {"form": form, "error": error})


def thank_you_view(request):
    return render(request, "main/thank_you.html")


def privacy_view(request):
    return render(request, "main/privacy.html")


def robots_txt(request):
    lines = [
        "User-agent: *",
        "Disallow: /admin/",
        "Allow: /$",
        "Allow: /privacy/",
    ]
    return HttpResponse("\n".join(lines), content_type="text/plain")


def redirect_to_destination(request, card_id):
    """
    domain.com/CARDID -> looks up the card and 302s to its destination.
    Unknown / inactive / not-yet-set cards get a friendly fallback page, not a raw error.
    """
    card_id_clean = card_id.strip().upper()
    card = Card.objects.filter(card_id=card_id_clean, is_active=True).first()

    if not card or not card.destination:
        return render(request, "main/card_inactive.html", status=404)

    response = redirect(card.destination)
    # Never let browsers cache this — admin may change the destination at any time.
    response["Cache-Control"] = "no-store"
    return response
