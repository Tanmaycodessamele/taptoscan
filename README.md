# Card Manager (nfc project)

A one-page redirect manager: card ID + password + destination URL.
Visiting `yourdomain.in/CARDID` 302-redirects to whatever destination
the owner last set. No user accounts — the card password IS the access
control.

## What's included

- `main/models.py` — the `Card` model. Password is hashed (Django's
  built-in hasher), never stored in plain text. Destination is
  validated to be `http://`/`https://` **in the form, in the model,
  and as a raw database CHECK constraint** — three independent layers,
  so no request can bypass it.
- `main/views.py` — the management form (`/`) and the redirect view
  (`/<CARDID>/`, must stay last in `urls.py`). The redirect sends
  `Cache-Control: no-store` so browsers never cache a stale
  destination.
- `main/admin.py` — go to `/admin/` → Cards → "Add card" to generate a
  new card. The ID and password are auto-generated and the password is
  shown **once**, in a banner, right after you save. Write it down —
  it's stored only as a hash after that.
- Custom 404 page, a "card not set up yet" fallback for unknown/blank
  cards, a thank-you page, `robots.txt`, per-page titles/meta
  descriptions, 5 FAQs on the form page, and a Privacy Policy page
  (placeholders inside — see below).
- `whitenoise` for serving static files in production without a
  separate static file host.
- Google Analytics: wired up but inactive until you set
  `GA_MEASUREMENT_ID` in `.env` — leave it blank to keep it off.

## What I deliberately left out (said so, per your instructions)

- **Social share image, team photo, real reviews, case studies, maps —
  need real assets/content I don't have.** Add them yourself when
  ready; ask me and I'll wire them in.
- **Local business schema (JSON-LD)** — needs a real business
  name/address/phone; tell me these and I'll add it.
- **CTA-above-fold / sticky mobile CTA / breadcrumbs / internal
    linking / response-time promise** — these are marketing-site
  patterns that don't fit a single-purpose utility form; skipped as
  not applicable to this app's structure.
- **Rate limiting / DDoS protection** — this is Cloudflare's job, not
  Django's, per what we discussed. Set it up in the Cloudflare
  dashboard once your domain is on it (a rate-limit rule on `/` and
  on `/<card_id>/`).

## Running it locally

```bash
python -m venv venv
# Windows:  venv\Scripts\activate
source venv/bin/activate

pip install -r requirements.txt

cp .env.example .env
# open .env and set SECRET_KEY — generate one with:
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"

python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Then:
- `http://127.0.0.1:8000/` — the card management form
- `http://127.0.0.1:8000/admin/` — log in, add a card, copy the
  generated password
- `http://127.0.0.1:8000/CARDID/` — test the redirect once you've set
  a destination on that card

## Deploying (e.g. Railway)

1. Push this project to a GitHub repo (or connect Railway directly to
   it).
2. In Railway: New Project → Deploy from GitHub → add this repo.
3. Add a PostgreSQL database in the same project — Railway sets
   `DATABASE_URL` automatically; the settings file already reads it.
4. Set environment variables in Railway's dashboard (mirror
   `.env.example`): `SECRET_KEY` (generate a real one — see above),
   `DEBUG=False`, `ALLOWED_HOSTS=yourdomain.in,www.yourdomain.in`,
   `CSRF_TRUSTED_ORIGINS=https://yourdomain.in,https://www.yourdomain.in`,
   `SITE_NAME`, `CONTACT_EMAIL`.
5. Railway runs `pip install -r requirements.txt` automatically and
   uses the `Procfile` (`web:` process + a `release:` step that runs
   migrations on every deploy).
6. Point your domain at Railway (custom domain settings), then set
   your registrar's DNS through Cloudflare as discussed.
7. Run `python manage.py createsuperuser` once, via Railway's shell
   (Railway dashboard → your service → "Shell" / or the Railway CLI),
   to create your own admin login.
8. Visit `/admin/` on your live domain and start creating cards.

## Before you print real cards

- Double-check `DEBUG=False` and `SECRET_KEY` is a real generated
  value, not the placeholder.
- Fill in `main/templates/main/privacy.html` — replace `[ADD DATE]`
  and the contact email; it's a starting template, not legal advice.
- Test one full real card end-to-end on the live domain before
  printing a batch.
