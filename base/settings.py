from pathlib import Path
from datetime import timedelta

import os

from dotenv import load_dotenv

from base import utils

load_dotenv()

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# If this causes an error, you need to have a .env file with the secret key in it.
SECRET_KEY = os.getenv("DJANGO_SECRET")

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = int(os.getenv("DJANGO_DEBUG", 1)) == 1

# This is ignored when DEBUG = True.
ALLOWED_HOSTS = ["localhost", "127.0.0.1", os.getenv("DOMAIN")]

# Application definition

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.humanize",  # App added to allow for the use of intcomma in templates
    "apps.accounts",
    "apps.finances",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "base.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [
            os.path.join(BASE_DIR, "templates")
        ],  # add this so templates can be found within app
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "base.context_processors.notifications",
            ],
        },
    },
]

WSGI_APPLICATION = "base.wsgi.application"


# Database
# https://docs.djangoproject.com/en/5.2/ref/settings/#databases

DB_TEMPLATE_SQLITE = {
    "ENGINE": "django.db.backends.sqlite3",
    "NAME": os.getenv("DATABASE_NAME", BASE_DIR / "db.sqlite3"),
}

DATABASE_MYSQL_SSL_CA = os.getenv("DATABASE_MYSQL_SSL_CA", None)

DB_TEMPLATE_MYSQL_OPTIONS = {"OPTIONS": {"ssl": {"ca": DATABASE_MYSQL_SSL_CA}}}

DB_TEMPLATE_MYSQL = {
    "ENGINE": "django.db.backends.mysql",
    "NAME": os.getenv("DATABASE_NAME"),
    "USER": os.getenv("DATABASE_USERNAME"),
    "PASSWORD": os.getenv("DATABASE_PASSWORD"),
    "HOST": os.getenv("DATABASE_HOST"),
    "PORT": os.getenv("DATABASE_PORT", 3306),
}

DATABASE_ENGINE = os.getenv("DATABASE_ENGINE")

match DATABASE_ENGINE:
    case "sqlite3":
        DB_TEMPLATE = DB_TEMPLATE_SQLITE
    case "mysql":
        if DATABASE_MYSQL_SSL_CA:
            DB_TEMPLATE = dict(DB_TEMPLATE_MYSQL, **DB_TEMPLATE_MYSQL_OPTIONS)
        else:
            DB_TEMPLATE = DB_TEMPLATE_MYSQL
    case _:
        raise EnvironmentError(
            "Invalid database engine selected; must be one of [mysql, sqlite3]"
        )

DATABASES = {"default": DB_TEMPLATE}

# Password validation
# https://docs.djangoproject.com/en/5.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]


# Internationalization
# https://docs.djangoproject.com/en/5.2/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "America/New_York"

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.2/howto/static-files/

# For actual production servers and LiveServerTestCase tests STATIC_ROOT must be set for the server to read static files from.
# Run collectstatic before testing. It will create the directory "staticfiles/" for you. This folder is in the gitignore.
STATIC_ROOT = (
    os.path.join(BASE_DIR, "staticfiles") if DEBUG else os.getenv("STATIC_DIR")
)
# URL for the server to retrieve static files. ANYTHING IN STATIC IS ACCESSIBLE TO THE USER BY A PATH. (/static/css/base.css, for example)
STATIC_URL = "/static/"
# This is where the development server finds static files. Also, collectstatic finds files in here to put in STATIC_ROOT.
STATICFILES_DIRS = [os.path.join(BASE_DIR, "static")]

# Default primary key field type
# https://docs.djangoproject.com/en/5.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# Where Django redirects you if try to go to a url that requires authentication without logging in first
# This is already by default, but this is added to make the default clear.
LOGIN_URL = "login"

# After login, redirect users here
LOGIN_REDIRECT_URL = "dashboard"

# After logout, redirect users here
LOGOUT_REDIRECT_URL = "home"

AUTH_USER_MODEL = "accounts.UserAccount"

# Global email authentication setting
# This is a dynamic setting; it doesn't change what is migrated
EMAIL_AUTHENTICATION = True

# This has to point to a class that extends base.utils.EmailBackend
# EMAIL_BACKEND = utils.SesEmailBackend # do not use this unless you really need to
EMAIL_BACKEND = (
    utils.SesEmailBackend
    if os.getenv("EMAIL_BACKEND") == "ses"
    else utils.DummyEmailBackend
)

# This is specifically for test cases, so that auth code messages don't flood the test output
DUMMY_AUTH_BACKEND_QUIET = False

# Email addresses
EMAIL_AUTHENTICATION_ADDRESS = os.getenv("EMAIL_AUTH_SENDING_ADDRESS")

# Maximum authentication age before a user must regenerate a new code
AUTH_SESSION_MAX_AGE = timedelta(seconds=int(os.getenv("AUTH_SESSION_MAX_AGE")))

# What to display when telling the user that age
AUTH_SESSION_MAX_AGE_STRING = os.getenv("AUTH_SESSION_MAX_AGE_STRING")
