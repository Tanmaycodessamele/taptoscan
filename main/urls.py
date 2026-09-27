from django.urls import path

from . import views

urlpatterns = [
    path("", views.manage_view, name="manage"),
    path("thank-you/", views.thank_you_view, name="thank_you"),
    path("privacy/", views.privacy_view, name="privacy"),
    path("robots.txt", views.robots_txt, name="robots_txt"),
    # Must stay LAST: catches domain.com/CARDID for the actual redirect.
    path("<str:card_id>/", views.redirect_to_destination, name="redirect_card"),
]
