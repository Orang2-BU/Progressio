import os
from datetime import timedelta
from pathlib import Path
from dotenv import load_dotenv
from django.core.exceptions import ImproperlyConfigured

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Load environment variables from .env file
load_dotenv(BASE_DIR / '.env')

# Quick-start development settings - unsuitable for production
SECRET_KEY = os.getenv('SECRET_KEY', 'django-insecure-progressio-development-secret-key-change-in-production-2026')

DEBUG = os.getenv('DEBUG', 'True') == 'True'

ALLOWED_HOSTS = [host.strip() for host in os.getenv('ALLOWED_HOSTS', '*').split(',') if host.strip()]
PUBLIC_WEB_URL = os.getenv('PUBLIC_WEB_URL', '').rstrip('/')

# How many reverse proxies sit in front of this application. Zero means the
# client address is REMOTE_ADDR and X-Forwarded-For is ignored entirely, which
# is the safe default: a client that may send the header could otherwise mint a
# fresh request budget per request. Set it only together with an edge proxy that
# REPLACES the inbound header. See back-end/THROTTLING.md.
try:
    TRUSTED_PROXY_COUNT = int(os.getenv('TRUSTED_PROXY_COUNT', '0') or 0)
except ValueError as exc:
    raise ImproperlyConfigured('TRUSTED_PROXY_COUNT must be a whole number.') from exc
if TRUSTED_PROXY_COUNT < 0:
    raise ImproperlyConfigured('TRUSTED_PROXY_COUNT cannot be negative.')


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Third party apps
    'rest_framework',
    'rest_framework_simplejwt',
    'corsheaders',
    'django_filters',
    'drf_spectacular',

    # Progressio Domain Apps
    'apps.common',
    'apps.accounts',
    'apps.curriculum',
    'apps.careers',
    'apps.competencies',
    'apps.skills',
    'apps.learning',
    'apps.assessments',
    'apps.credentials',
    'apps.verification',
    'apps.ai',
    'apps.blockchain',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'


# Custom User Model
AUTH_USER_MODEL = 'accounts.User'


# Database Configuration
db_engine = os.getenv('DB_ENGINE', 'postgresql')
if db_engine == 'sqlite':
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': os.getenv('DB_NAME', 'progressio_db'),
            'USER': os.getenv('DB_USER', 'progressio'),
            'PASSWORD': os.getenv('DB_PASSWORD', 'progressio_dev_2026'),
            'HOST': os.getenv('DB_HOST', 'localhost'),
            'PORT': os.getenv('DB_PORT', '5432'),
        }
    }


# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True


# Static files (CSS, JavaScript, Images)
STATIC_URL = 'static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


# Request budgets (throttling)
#
# Two families, deliberately kept apart so guessing credentials cannot spend the
# budget reserved for graded work, and a student hammering an AI endpoint cannot
# lock themselves out of logging in. Every value is "<requests>/<period>" and
# every value is overridable per deployment; the reasoning behind each starting
# value lives in back-end/THROTTLING.md next to this list.
# DRF parses these periods by their first letter, so validate the whole token
# before passing it on; otherwise values like ``10/month`` silently mean 10/min.
THROTTLE_PERIODS = {
    's', 'sec', 'second', 'seconds',
    'm', 'min', 'minute', 'minutes',
    'h', 'hour', 'hours',
    'd', 'day', 'days',
}


def throttle_rate(env_name, default):
    """Read one budget from the environment, failing loudly when malformed."""
    raw = (os.getenv(env_name) or '').strip() or default
    count, _, period = raw.partition('/')
    period = period.strip().lower()
    if not count.strip().isdigit() or int(count) < 1 or period not in THROTTLE_PERIODS:
        raise ImproperlyConfigured(
            f'{env_name} must use a positive count and a supported period '
            '(s/sec/second, m/min/minute, h/hour, or d/day), '
            f'for example 10/min; got {raw!r}.'
        )
    return f'{int(count)}/{period}'


THROTTLE_RATES = {
    # Credential attempts.
    'auth_register': throttle_rate('THROTTLE_RATE_AUTH_REGISTER', '60/hour'),
    'auth_login': throttle_rate('THROTTLE_RATE_AUTH_LOGIN', '10/min'),
    'auth_login_ip': throttle_rate('THROTTLE_RATE_AUTH_LOGIN_IP', '60/min'),
    'auth_refresh': throttle_rate('THROTTLE_RATE_AUTH_REFRESH', '30/min'),
    # Work that can reach a provider or run a full grading pass.
    'expensive_assessment': throttle_rate('THROTTLE_RATE_ASSESSMENT_SUBMIT', '30/hour'),
    'expensive_ai': throttle_rate('THROTTLE_RATE_AI', '20/hour'),
    'expensive_credential': throttle_rate('THROTTLE_RATE_CREDENTIAL_ISSUE', '10/hour'),
    # Unauthenticated credential verification, which may call the proof provider.
    'public_verify': throttle_rate('THROTTLE_RATE_PUBLIC_VERIFY', '60/min'),
}


# Request budget counters.
#
# THROTTLE_CACHE_URL wins. Failing that, the Celery broker is reused, because
# the deployed profile already runs Redis and a budget only one of two web
# processes can see is not a budget. With neither set the counters are local to
# each process, which back-end/THROTTLING.md states as a limit of the design.
THROTTLE_CACHE_LOCATION = (
    os.getenv('THROTTLE_CACHE_URL', '').strip()
    or (os.getenv('CELERY_BROKER_URL', '').strip()
        if os.getenv('CELERY_BROKER_URL', '').strip().startswith('redis://') else '')
)
THROTTLE_CACHE_ALIAS = os.getenv('THROTTLE_CACHE_ALIAS', '').strip() or (
    'throttle' if THROTTLE_CACHE_LOCATION else 'default'
)
if not DEBUG and (not THROTTLE_CACHE_LOCATION or THROTTLE_CACHE_ALIAS == 'default'):
    raise ImproperlyConfigured(
        'DEBUG=False requires a shared Redis throttle cache; set THROTTLE_CACHE_URL '
        'or a Redis CELERY_BROKER_URL and do not set THROTTLE_CACHE_ALIAS=default.'
    )

CACHES: dict[str, dict[str, object]] = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'progressio-default',
    },
}
if THROTTLE_CACHE_ALIAS not in CACHES:
    CACHES[THROTTLE_CACHE_ALIAS] = {
        'BACKEND': 'django.core.cache.backends.redis.RedisCache',
        'LOCATION': THROTTLE_CACHE_LOCATION,
        'KEY_PREFIX': os.getenv('THROTTLE_CACHE_KEY_PREFIX', 'progressio'),
        # Only a fallback: every counter is written with its own window.
        'TIMEOUT': int(os.getenv('THROTTLE_CACHE_TIMEOUT', '300')),
    }


# Django REST Framework Settings
REST_FRAMEWORK = {
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.AllowAny',
    ],
    'DEFAULT_FILTER_BACKENDS': [
        'django_filters.rest_framework.DjangoFilterBackend',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
    # Published for DRF-adjacent tooling; the throttles in apps.common read the
    # top-level THROTTLE_RATES setting so one place owns every scope.
    'DEFAULT_THROTTLE_RATES': THROTTLE_RATES,
    # DRF's own NUM_PROXIES stays unset: apps.common.throttling decides which
    # forwarded addresses to trust, using TRUSTED_PROXY_COUNT.
    'EXCEPTION_HANDLER': 'apps.common.exception_handlers.api_exception_handler',
}

TEST_RUNNER = 'config.test_runner.ProgressioTestRunner'


# Simple JWT Settings
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=30),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ROTATE_REFRESH_TOKENS': False,
    'BLACKLIST_AFTER_ROTATION': False,
    'AUTH_HEADER_TYPES': ('Bearer',),
}


# DRF-Spectacular (OpenAPI 3.0) Settings
SPECTACULAR_SETTINGS = {
    'TITLE': 'Progressio API',
    'DESCRIPTION': 'Progressio - Turning Progress Into Proof. Technical Backend API (MVP v1.0).',
    'VERSION': '1.0.0',
    'SERVE_INCLUDE_SCHEMA': False,
    'COMPONENT_SPLIT_REQUEST': True,
    'SCHEMA_PATH_PREFIX': r'/api/v1/',
    'SWAGGER_UI_SETTINGS': {
        'deepLinking': True,
        'persistAuthorization': True,
        'displayOperationId': True,
    },
    'ENUM_NAME_OVERRIDES': {
        'SubmissionStatusEnum': 'apps.assessments.models.Submission.Status',
        'CredentialStatusEnum': 'apps.credentials.models.Credential.Status',
    },
}


# CORS Configuration
cors_origins = os.getenv('CORS_ALLOWED_ORIGINS', '')
if cors_origins:
    CORS_ALLOWED_ORIGINS = [origin.strip() for origin in cors_origins.split(',') if origin.strip()]
else:
    CORS_ALLOW_ALL_ORIGINS = True


# Email Backend Configuration
# For development: console backend. In production: configure SMTP.
EMAIL_BACKEND = os.getenv(
    'EMAIL_BACKEND',
    'django.core.mail.backends.console.EmailBackend'
)


# Celery Configuration
CELERY_BROKER_URL = os.getenv('CELERY_BROKER_URL', 'redis://localhost:6379/0')
CELERY_RESULT_BACKEND = os.getenv('CELERY_RESULT_BACKEND', 'redis://localhost:6379/0')
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = 'UTC'

