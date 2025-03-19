from pathlib import Path
from dotenv import load_dotenv
from os import getenv, path
from loguru import logger
from datetime import timedelta


# from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent

local_env_file = path.join(BASE_DIR, ".envs", ".env.local")

if path.isfile(local_env_file):
    load_dotenv(local_env_file)

# Application definition

DJANGO_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # "django.contrib.sites",
    "django.contrib.humanize",
]

THIRD_PARTY_APPS = [
    # "debug_toolbar",
    "rest_framework",
    "django_countries",
    "phonenumber_field",
    "drf_yasg",
    "corsheaders",
    "djoser",
    "django_filters",
    "djcelery_email",
    "rest_framework_simplejwt",
    "django.contrib.sites",  # Required for django-allauth
    "allauth",
    "allauth.account",
    "allauth.socialaccount",  # Optional: for social authentication
    "dj_rest_auth",
    "rest_framework.authtoken",
    "dj_rest_auth.registration",
    # "haystack",
    # "drf_haystack",
]

LOCAL_APPS = ["core_apps.common", "core_apps.users", "core_apps.profiles"]

INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.locale.LocaleMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "allauth.account.middleware.AccountMiddleware",
    # "debug_toolbar.middleware.DebugToolbarMiddleware",
]

AUTHENTICATION_BACKENDS = (
    "core_apps.users.backends.EmailOrUsernameBackend",  # custom authentication
    "allauth.account.auth_backends.AuthenticationBackend",  # Allows allauth authentication
)

ROOT_URLCONF = "core.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "core.wsgi.application"

# Database
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

PASSWORD_HASHERS = [
    "django.contrib.auth.hashers.Argon2PasswordHasher",
    "django.contrib.auth.hashers.PBKDF2PasswordHasher",
    "django.contrib.auth.hashers.PBKDF2SHA1PasswordHasher",
    "django.contrib.auth.hashers.BCryptSHA256PasswordHasher",
    "django.contrib.auth.hashers.ScryptPasswordHasher",
]

# Password validation
# https://docs.djangoproject.com/en/4.2/ref/settings/#auth-password-validators

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
# Redis Cache Configuration
CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://127.0.0.1:6379/1",
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
            "PARSER_CLASS": "redis.connection.HiredisParser",
            "CONNECTION_POOL_KWARGS": {"max_connections": 100},
            "COMPRESSOR": "django_redis.compressors.zlib.ZlibCompressor",
            "IGNORE_EXCEPTIONS": True,
        },
        "KEY_PREFIX": "medium_clone",
    }
}

# Cache time to live is 15 minutes (in seconds)
CACHE_TTL = 60 * 15

# Session cache configuration
SESSION_ENGINE = "django.contrib.sessions.backends.cache"
SESSION_CACHE_ALIAS = "default"

# Celery Configuration
CELERY_BROKER_URL = "redis://127.0.0.1:6379/0"
CELERY_RESULT_BACKEND = "redis://127.0.0.1:6379/0"
CELERY_ACCEPT_CONTENT = ["application/json"]
CELERY_TASK_SERIALIZER = "json"
CELERY_RESULT_SERIALIZER = "json"
CELERY_TIMEZONE = "UTC"

CELERY_BROKER_URL = getenv("CELERY_BROKER")
CELERY_RESULT_BACKEND = getenv("CELERY_BACKEND")
CELERY_ACCEPT_CONTENT = ["json"]
CELERY_TASK_SERIALIZER = "json"
CELERY_RESULT_SERIALIZER = "json"
CELERY_TIMEZONE = "UTC"

# Django REST Framework settings
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework_simplejwt.authentication.JWTAuthentication",  # Fully stateless
    ],
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticated",  # Require authentication for all endpoints
    ],
    "DEFAULT_FILTER_BACKENDS": [
        "django_filters.rest_framework.DjangoFilterBackend",  # For field filtering
        "rest_framework.filters.SearchFilter",  # For search functionality
        "rest_framework.filters.OrderingFilter",  # For ordering results
    ],
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",  # Enable pagination
    "PAGE_SIZE": 10,
    "PAGE_SIZE_QUERY_PARAM": "page_size",
    "MAX_PAGE_SIZE": 100,
    "DEFAULT_THROTTLE_CLASSES": [
        "rest_framework.throttling.AnonRateThrottle",  # Throttle anonymous users
        "rest_framework.throttling.UserRateThrottle",  # Throttle authenticated users
    ],
    "DEFAULT_THROTTLE_RATES": {
        "anon": "100/day",  # Anonymous users: 100 requests per day
        "user": "1000/day",  # Authenticated users: 1000 requests per day
    },
}

# Simple JWT settings
SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(
        minutes=30
    ),  # Access token lifetime (e.g., 30 minutes)
    "REFRESH_TOKEN_LIFETIME": timedelta(days=1),  # Refresh token lifetime (e.g., 1 day)
    "ROTATE_REFRESH_TOKENS": True,  # Automatically rotate refresh tokens
    "BLACKLIST_AFTER_ROTATION": False,  # No blacklisting
    "UPDATE_LAST_LOGIN": False,  # Update the user's last login time on token refresh
    "ALGORITHM": "HS256",  # Encryption algorithm
    "SIGNING_KEY": getenv("SECRET_KEY"),  # Use Django's SECRET_KEY for signing
    "VERIFYING_KEY": None,  # No verifying key for HS256
    "AUDIENCE": None,  # No audience
    "ISSUER": None,  # No issuer
    "AUTH_HEADER_TYPES": (
        "Bearer",
    ),  # Authorization header type (e.g., Bearer <token>)
    "USER_ID_FIELD": "id",  # Field to use as the user ID
    "USER_ID_CLAIM": "user_id",  # Claim to use as the user ID in the token
    "AUTH_TOKEN_CLASSES": (
        "rest_framework_simplejwt.tokens.AccessToken",
    ),  # Token classes
}
# dj-rest-auth
REST_AUTH = {
    "USE_JWT": True,  # Newer syntax (v6.0.0), redundant with above but explicit
    "JWT_AUTH_COOKIE": None,  # No cookie-based JWT (optional)
    "JWT_AUTH_REFRESH_COOKIE": None,
    "REGISTER_SERIALIZER": "core_apps.users.serializers.CustomRegisterSerializer",
    "LOGIN_SERIALIZER": "your_app.serializers.CustomLoginSerializer",
    "PASSWORD_RESET_SERIALIZER": "core_apps.users.serializers.CustomPasswordResetSerializer",
    "PASSWORD_RESET_CONFIRM_SERIALIZER": "core_apps.users.serializers.CustomPasswordResetConfirmSerializer",
    "PASSWORD_CHANGE_SERIALIZER": "core_apps.users.serializers.CustomPasswordChangeSerializer",
    "USER_DETAILS_SERIALIZER": "core_apps.users.serializers.UserDetailsSerializer",
}

ACCOUNT_AUTHENTICATION_METHOD = "username_email"  # Allow both username and email
ACCOUNT_EMAIL_REQUIRED = True  # Require email for signup
ACCOUNT_UNIQUE_EMAIL = True  # Ensure email is unique
ACCOUNT_USERNAME_REQUIRED = True  # Make username mandatory
ACCOUNT_EMAIL_VERIFICATION = "mandatory"  # Require email verification
ACCOUNT_EMAIL_CONFIRMATION_EXPIRE_DAYS = 3  # Expiration for confirmation emails

AUTH_USER_MODEL = "users.User"

LANGUAGE_CODE = "fa-ir"

TIME_ZONE = "UTC"

USE_I18N = True

USE_TZ = True

SITE_ID = 1

ADMIN_URL = "secretgateway/"

STATIC_URL = "/static/"

STATIC_ROOT = str(BASE_DIR / "staticfiles")

MEDIA_URL = "/mediafiles/"

MEDIA_ROOT = str(BASE_DIR / "mediafiles")

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

CORS_URLS_REGEX = r"^/api/.*$"

LOGGING_CONFIG = None

LOGURU_LOGGING = {
    "handlers": [
        {
            "sink": BASE_DIR / "logs/debug.log",
            "level": "DEBUG",
            "filter": lambda record: record["level"].no <= logger.level("WARNING").no,
            "format": "{time:YYYY-MM-DD HH:mm:ss.SSS} | {level: <8} | {name}:{function}:{line} - "
            "{message}",
            "rotation": "10MB",
            "retention": "30 days",
            "compression": "zip",
        },
        {
            "sink": BASE_DIR / "logs/error.log",
            "level": "ERROR",
            "format": "{time:YYYY-MM-DD HH:mm:ss.SSS} | {level: <8} | {name}:{function}:{line} - "
            "{message}",
            "rotation": "10MB",
            "retention": "30 days",
            "compression": "zip",
            "backtrace": True,
            "diagnose": True,
        },
    ],
}
logger.configure(**LOGURU_LOGGING)

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {"loguru": {"class": "interceptor.InterceptHandler"}},
    "root": {"handlers": ["loguru"], "level": "DEBUG"},
}
