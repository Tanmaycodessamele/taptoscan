from django.conf import settings


def site_settings(request):
    """Makes site-wide values available in every template (base.html, titles, GA, etc.)."""
    return {
        "SITE_NAME": getattr(settings, "SITE_NAME", "Card Manager"),
        "CONTACT_EMAIL": getattr(settings, "CONTACT_EMAIL", ""),
        "GA_ID": getattr(settings, "GA_MEASUREMENT_ID", ""),
    }
