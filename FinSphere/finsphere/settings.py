import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
SECRET_KEY = os.environ.get("DJANGO_SECRET_KEY", "dev-only-secret-change-me-before-deploying-0123456789")
DEBUG = os.environ.get("DJANGO_DEBUG", "1") == "1"
ALLOWED_HOSTS = ["*"] if DEBUG else os.environ.get("ALLOWED_HOSTS", "").split(",")

INSTALLED_APPS = [
    "django.contrib.admin", "django.contrib.auth", "django.contrib.contenttypes",
    "django.contrib.sessions", "django.contrib.messages", "django.contrib.staticfiles", "core",
]
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware", "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware", "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware", "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]
ROOT_URLCONF = "finsphere.urls"
TEMPLATES = [{
    "BACKEND": "django.template.backends.django.DjangoTemplates", "DIRS": [], "APP_DIRS": True,
    "OPTIONS": {"context_processors": [
        "django.template.context_processors.request", "django.contrib.auth.context_processors.auth",
        "django.contrib.messages.context_processors.messages"]},
}]
WSGI_APPLICATION = "finsphere.wsgi.application"
DATABASES = {"default": {"ENGINE": "django.db.backends.sqlite3", "NAME": BASE_DIR / "db.sqlite3"}}
AUTH_PASSWORD_VALIDATORS = [{"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
                            {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"}]
LANGUAGE_CODE, TIME_ZONE, USE_I18N, USE_TZ = "en-us", "Asia/Kolkata", True, True
STATIC_URL = "static/"
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
LOGIN_URL = "login"

DATASET_PATH = BASE_DIR / "Dataset" / "budget.csv"

# OTP e-mail: prints the code in the VS Code terminal by default.
# For real e-mail set EMAIL_HOST_USER / EMAIL_HOST_PASSWORD (e.g. a Gmail app-password).
if os.environ.get("EMAIL_HOST_USER"):
    EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
    EMAIL_HOST, EMAIL_PORT, EMAIL_USE_TLS = "smtp.gmail.com", 587, True
    EMAIL_HOST_USER = os.environ["EMAIL_HOST_USER"]
    EMAIL_HOST_PASSWORD = os.environ.get("EMAIL_HOST_PASSWORD", "")
    DEFAULT_FROM_EMAIL = EMAIL_HOST_USER
else:
    EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
    DEFAULT_FROM_EMAIL = "FinSphere <no-reply@finsphere.local>"
