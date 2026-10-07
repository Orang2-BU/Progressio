import os
import ipaddress
import re
from datetime import timedelta
from email.utils import parseaddr
from pathlib import Path
from urllib.parse import urlsplit
from dotenv import load_dotenv

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Load environment variables from .env file
load_dotenv(BASE_DIR / '.env')


def is_explicit_host(host):
    if not host or host != host.strip() or '*' in host or host.startswith('.') or '/' in host or '@' in host:
        return False
    try:
        ipaddress.ip_address(host.strip('[]'))
        return True
    except ValueError:
        labels = host.rstrip('.').split('.')
        return len(host) <= 253 and all(
            label and len(label) <= 63 and re.fullmatch(r'[A-Za-z0-9](?:[A-Za-z0-9-]*[A-Za-z0-9])?', label)
            for label in labels
        )


APP_ENV = os.getenv('APP_ENV', '').strip().lower()
if APP_ENV not in {'local', 'production'}:
    raise ValueError("Set APP_ENV explicitly to either 'local' or 'production'.")

if APP_ENV == 'production':
    if os.getenv('DB_ENGINE', 'postgresql').strip().lower() != 'postgresql':
        raise ValueError("DB_ENGINE must be 'postgresql' when APP_ENV=production.")
    required = (
        'SECRET_KEY', 'ALLOWED_HOSTS', 'CORS_ALLOWED_ORIGINS',
        'CSRF_TRUSTED_ORIGINS', 'DB_NAME', 'DB_USER', 'DB_PASSWORD', 'DB_HOST',
    )
    missing = [name for name in required if not os.getenv(name, '').strip()]
    if missing:
        raise ValueError(f"APP_ENV=production requires: {', '.join(missing)}")
    SECRET_KEY = os.environ['SECRET_KEY']
    if len(SECRET_KEY) < 50 or len(set(SECRET_KEY)) < 5 or SECRET_KEY.startswith('django-insecure-'):
        raise ValueError('Production SECRET_KEY must be a unique secret of at least 50 characters.')
    DEBUG = os.getenv('DEBUG', 'False').lower() in {'1', 'true', 'yes', 'on'}
    if DEBUG:
        raise ValueError('DEBUG must be False when APP_ENV=production.')
    ALLOWED_HOSTS = [host.strip() for host in os.environ['ALLOWED_HOSTS'].split(',') if host.strip()]
    if not ALLOWED_HOSTS or any(not is_explicit_host(host) for host in ALLOWED_HOSTS):
        raise ValueError('Production ALLOWED_HOSTS must list explicit hosts and cannot contain wildcards.')
else:
    SECRET_KEY = os.getenv('SECRET_KEY', 'django-insecure-local-only-development-key')
    DEBUG = os.getenv('DEBUG', 'True').lower() in {'1', 'true', 'yes', 'on'}
    ALLOWED_HOSTS = [host.strip() for host in os.getenv('ALLOWED_HOSTS', 'localhost,127.0.0.1,0.0.0.0,backend').split(',') if host.strip()]

if APP_ENV == 'production':
    AI_PROVIDER = os.getenv('AI_PROVIDER', '').strip().lower()
    BLOCKCHAIN_PROVIDER = os.getenv('BLOCKCHAIN_PROVIDER', '').strip().lower()
    if AI_PROVIDER not in {'mock', 'openai'}:
        raise ValueError("Production requires AI_PROVIDER to be explicitly set to 'mock' or 'openai'.")
    if BLOCKCHAIN_PROVIDER not in {'mock', 'http'}:
        raise ValueError("Production requires BLOCKCHAIN_PROVIDER to be explicitly set to 'mock' or 'http'.")
    if AI_PROVIDER == 'openai' and not os.getenv('OPENAI_API_KEY', '').strip():
        raise ValueError('OPENAI_API_KEY is required when production AI_PROVIDER=openai.')
    if BLOCKCHAIN_PROVIDER == 'http' and not os.getenv('BLOCKCHAIN_SERVICE_URL', '').strip():
        raise ValueError('BLOCKCHAIN_SERVICE_URL is required when production BLOCKCHAIN_PROVIDER=http.')
    if os.getenv('AI_ALLOW_MOCK_FALLBACK', 'False').lower() in {'1', 'true', 'yes', 'on'}:
        raise ValueError('AI_ALLOW_MOCK_FALLBACK must be False in production.')

PUBLIC_WEB_URL = os.getenv('PUBLIC_WEB_URL', '').rstrip('/')


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
}


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
def is_https_origin(origin):
    parsed = urlsplit(origin)
    try:
        port_is_valid = parsed.port is None or 1 <= parsed.port <= 65535
    except ValueError:
        return False
    return (
        parsed.scheme == 'https'
        and is_explicit_host(parsed.hostname or '')
        and port_is_valid
        and parsed.username is None
        and parsed.password is None
        and parsed.path in ('', '/')
        and not parsed.query
        and not parsed.fragment
    )


cors_origins = os.getenv('CORS_ALLOWED_ORIGINS', '')
if cors_origins:
    CORS_ALLOWED_ORIGINS = [origin.strip() for origin in cors_origins.split(',') if origin.strip()]
    if APP_ENV == 'production' and (not CORS_ALLOWED_ORIGINS or any(not is_https_origin(origin) for origin in CORS_ALLOWED_ORIGINS)):
        raise ValueError('Production CORS_ALLOWED_ORIGINS must contain explicit HTTPS origins without paths or wildcards.')
else:
    CORS_ALLOW_ALL_ORIGINS = APP_ENV == 'local'

if APP_ENV == 'production':
    CSRF_TRUSTED_ORIGINS = [origin.strip() for origin in os.environ['CSRF_TRUSTED_ORIGINS'].split(',') if origin.strip()]
    if not CSRF_TRUSTED_ORIGINS or any(not is_https_origin(origin) for origin in CSRF_TRUSTED_ORIGINS):
        raise ValueError('Production CSRF_TRUSTED_ORIGINS must contain explicit HTTPS origins without paths or wildcards.')
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_HSTS_SECONDS = int(os.getenv('SECURE_HSTS_SECONDS', '31536000'))
    if SECURE_HSTS_SECONDS <= 0:
        raise ValueError('Production SECURE_HSTS_SECONDS must be greater than zero.')
    SECURE_HSTS_INCLUDE_SUBDOMAINS = os.getenv('SECURE_HSTS_INCLUDE_SUBDOMAINS', 'False').lower() in {'1', 'true', 'yes', 'on'}
    SECURE_HSTS_PRELOAD = os.getenv('SECURE_HSTS_PRELOAD', 'False').lower() in {'1', 'true', 'yes', 'on'}
    # Only enable this behind a proxy that strips client-supplied X-Forwarded-Proto.
    if os.getenv('TRUST_X_FORWARDED_PROTO', '').lower() in {'1', 'true', 'yes', 'on'}:
        SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

    ENABLE_EMAIL = os.getenv('ENABLE_EMAIL', 'False').lower() in {'1', 'true', 'yes', 'on'}
    EMAIL_BACKEND = os.getenv('EMAIL_BACKEND', '').strip() or (
        'django.core.mail.backends.smtp.EmailBackend' if ENABLE_EMAIL
        else 'django.core.mail.backends.dummy.EmailBackend'
    )
    if ENABLE_EMAIL and EMAIL_BACKEND != 'django.core.mail.backends.smtp.EmailBackend':
        raise ValueError('ENABLE_EMAIL=True requires the SMTP email backend in production.')
    if ENABLE_EMAIL and EMAIL_BACKEND == 'django.core.mail.backends.smtp.EmailBackend':
        smtp_missing = [name for name in ('EMAIL_HOST', 'EMAIL_HOST_USER', 'EMAIL_HOST_PASSWORD') if not os.getenv(name, '').strip()]
        if smtp_missing:
            raise ValueError(f"ENABLE_EMAIL=True with SMTP requires: {', '.join(smtp_missing)}")
        sender = os.getenv('DEFAULT_FROM_EMAIL', '').strip()
        if not sender or '.invalid' in sender.lower():
            raise ValueError('ENABLE_EMAIL=True with SMTP requires a real DEFAULT_FROM_EMAIL sender address.')
        sender_address = parseaddr(sender)[1]
        sender_local, separator, sender_domain = sender_address.rpartition('@')
        if not separator or not sender_local or not is_explicit_host(sender_domain):
            raise ValueError('DEFAULT_FROM_EMAIL must contain a valid sender address when production email is enabled.')


# Email Backend Configuration
# For development: console backend. In production: configure SMTP.
if APP_ENV == 'local':
    EMAIL_BACKEND = os.getenv('EMAIL_BACKEND', 'django.core.mail.backends.console.EmailBackend')
EMAIL_HOST = os.getenv('EMAIL_HOST', '')
EMAIL_PORT = int(os.getenv('EMAIL_PORT', '587'))
EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER', '')
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD', '')
EMAIL_USE_TLS = os.getenv('EMAIL_USE_TLS', 'True').lower() in {'1', 'true', 'yes', 'on'}
DEFAULT_FROM_EMAIL = os.getenv('DEFAULT_FROM_EMAIL', 'Progressio <noreply@example.invalid>')

if APP_ENV == 'production':
    LOGGING = {
        'version': 1,
        'disable_existing_loggers': False,
        'handlers': {'console': {'class': 'logging.StreamHandler'}},
        'root': {'handlers': ['console'], 'level': os.getenv('LOG_LEVEL', 'INFO').upper()},
    }


# Celery Configuration
CELERY_BROKER_URL = os.getenv('CELERY_BROKER_URL', 'redis://localhost:6379/0')
CELERY_RESULT_BACKEND = os.getenv('CELERY_RESULT_BACKEND', 'redis://localhost:6379/0')
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = 'UTC'

