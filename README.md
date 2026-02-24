# Django Backend Template

A production-ready Django REST API template with:

- **HMAC + JWT authentication** (device-based, stateless, replay-attack resistant)
- **Health check endpoints** for Kubernetes liveness/readiness probes
- **Redis cache helpers** (set/get/delete with error fallback)
- **Custom DRF exception handler** (consistent error response format)
- **Tiered IP-based rate limiting** (burst, sustained, auth, search, etc.)
- **OpenAPI/Swagger docs** (drf-spectacular, served at obfuscated URL)
- **CMS dashboard** (Django admin + custom HTML dashboard for user management)
- **MySQL database** with `utf8mb4` charset
- **Docker + entrypoint.sh** (waits for MySQL, optionally runs migrations)
- **GitHub Actions CI/CD** (build & push to GHCR, deploy via self-hosted runner)

---

## Quick Start

```bash
# 1. Clone the template
git clone https://github.com/YOUR_ORG/YOUR_REPO.git myproject
cd myproject

# 2. Set up environment
cp .env.example .env
# Edit .env with your values

# 3. Create and activate a virtual environment
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 4. Run migrations
python manage.py makemigrations
python manage.py migrate

# 5. Create a superuser (for CMS access)
python manage.py createsuperuser

# 6. Start the development server
python manage.py runserver
```

### Via Docker Compose

```bash
cp .env.example .env   # edit first
docker compose up -d
```

---

## Project Structure

```
.
├── core/                  # Django project config (settings, root URLs, wsgi/asgi)
├── api/                   # Django application
│   ├── models.py          # User, UserProfile, Device + your project models
│   ├── views.py           # CMS views (dashboard, user management)
│   ├── forms.py           # CMS forms
│   ├── admin.py           # Django admin registrations
│   ├── utils.py           # Response helpers, cache wrappers, pagination
│   ├── throttling.py      # Rate-limiting classes
│   ├── exceptions.py      # Custom DRF exception handler
│   ├── health.py          # /health/, /health/ready/, /health/live/
│   ├── apis/
│   │   ├── auth/          # HMAC + JWT auth endpoints
│   │   ├── onboarding/    # Device registration
│   │   └── example/       # Example CRUD API (reference — delete when ready)
│   └── cron/
│       ├── example_cron.py  # Example cron job stub
│       └── helper.py        # Cron helpers
├── templates/             # HTML templates for CMS
├── Dockerfile
├── entrypoint.sh
└── .github/workflows/django.yml
```

---

## Adding a Feature

1. **Add a model** in `api/models.py` (uncomment the `Category`/`Item` stubs or write your own)
2. **Create migrations**: `python manage.py makemigrations && python manage.py migrate`
3. **Add serializers** in `api/apis/onboarding/serializers.py` (or a new file)
4. **Add an API view** — copy `api/apis/example/example.py` and rename/adapt
5. **Register the URL** in `api/urls.py`:
   ```python
   path("items/", include("api.apis.items.urls")),
   ```
6. **Register in admin**: add to `api/admin.py`
7. **(Optional) Add to CMS**: add views to `api/views.py`, forms to `api/forms.py`, URLs to `core/urls.py`

---

## API Authentication Flow

All mobile API calls follow this flow:

1. **Register device** — `POST /api/v1/device/register/` on first app launch
2. **Get JWT tokens** — `POST /api/v1/auth/get-token/` with HMAC-signed payload
3. **Access protected endpoints** — `Authorization: Bearer <access_token>`
4. **Refresh token** — `POST /api/v1/auth/refresh-token/` before access token expires

See `api/apis/auth/` for the full implementation.

---

## Rate Limiting

| Scope | Rate | Used On |
|---|---|---|
| `burst` (global) | 60/min | All endpoints |
| `sustained` (global) | 1000/hour | All endpoints |
| `auth_token` | 5/min | Auth endpoints |
| `data_modification` | 30/min | POST/PUT/PATCH |
| `content_listing` | 30/min | Feed/list endpoints |
| `search` | 20/min | Search endpoints |
| `admin` | 100/hour | Admin operations |

---

## Environment Variables

See [.env.example](.env.example) for the full list with descriptions.

---

## CI/CD Setup

1. Open `.github/workflows/django.yml`
2. Replace `YOUR_ORG/YOUR_REPO` with your GitHub org and repo name
3. Replace `your-runner-label` with your self-hosted runner's label (or `ubuntu-latest` for cloud runners)
4. Add your environment secrets to GitHub repository settings

---

## Health Endpoints

| Endpoint | Auth | Purpose |
|---|---|---|
| `GET /health/` | None | Checks DB + Redis. Returns 503 if unhealthy. |
| `GET /health/ready/` | None | DB readiness check (Kubernetes readiness probe) |
| `GET /health/live/` | None | Always returns 200 (Kubernetes liveness probe) |
