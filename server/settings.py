import os
from typing import List

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


DEBUG = True
ALLOWED_HOSTS: List[str] = []
# Random secret key - DO NOT USE if you intend to expose this server publicly. Instead,
# generate a new key (and make sure you don't check it into version control).
SECRET_KEY = "r07-4+21yggy$!cax)_3or)4^6_lx)l2!63^s=0!lvmn^o!jke"


INSTALLED_APPS = [
    "server.admin.KhaganateAdminConfig",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.humanize",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
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


ROOT_URLCONF = "server.urls"


TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [os.path.join(BASE_DIR, "server", "templates")],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ]
        },
    }
]


WSGI_APPLICATION = "server.wsgi.application"


# Database
# https://docs.djangoproject.com/en/2.2/ref/settings/#databases
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": os.path.join(BASE_DIR, "db.sqlite3"),
    }
}


# Internationalization
# https://docs.djangoproject.com/en/2.2/topics/i18n/
LANGUAGE_CODE = "en-us"
TIME_ZONE = "America/New_York"
USE_I18N = False
USE_L10N = False
USE_TZ = True


# Static files
# https://docs.djangoproject.com/en/2.2/howto/static-files/
STATIC_URL = "/static/"
STATICFILES_DIRS = [os.path.join(BASE_DIR, "server", "static")]


# Miscellaneous other settings
APPEND_SLASH = False
