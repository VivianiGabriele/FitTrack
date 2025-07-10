"""
Django settings for FitTrack project.

Optimized for Railway deployment
"""

import os
import sys
import logging
from pathlib import Path
import dj_database_url

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Setup emergency logging
logging.basicConfig(
    stream=sys.stderr,
    level=logging.DEBUG,
    format='%(asctime)s %(levelname)s %(message)s'
)
logger = logging.getLogger(__name__)

try:
    # SECURITY WARNING: keep the secret key used in production secret!
    SECRET_KEY = os.getenv('SECRET_KEY', 'django-insecure-development-key')

    # SECURITY WARNING: don't run with debug turned on in production!
    DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'

    # Railway automatically sets RAILWAY_ENVIRONMENT='production'
    if os.getenv('RAILWAY_ENVIRONMENT') == 'production':
        DEBUG = False

    ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', '*').split(',')
    CSRF_TRUSTED_ORIGINS = os.getenv('CSRF_TRUSTED_ORIGINS', '').split(',')

    # Database configuration
    DATABASES = {
        'default': dj_database_url.config(
            default=os.getenv('DATABASE_URL'),
            conn_max_age=600,
            ssl_require=os.getenv('DB_SSL', 'True') == 'True'
        )
    }

    # Application definition
    INSTALLED_APPS = [
        'django.contrib.admin',
        'django.contrib.auth',
        'django.contrib.contenttypes',
        'django.contrib.sessions',
        'django.contrib.messages',
        'django.contrib.staticfiles',
        
        # 3rd Party
        "crispy_forms",
        "crispy_bootstrap5",

        # Local apps
        'users',
        'workouts',
        'reminders',
        'goals',
    ]

    MIDDLEWARE = [
        'django.middleware.security.SecurityMiddleware',
        'whitenoise.middleware.WhiteNoiseMiddleware',
        'django.contrib.sessions.middleware.SessionMiddleware',
        'django.middleware.common.CommonMiddleware',
        'django.middleware.csrf.CsrfViewMiddleware',
        'django.contrib.auth.middleware.AuthenticationMiddleware',
        'django.contrib.messages.middleware.MessageMiddleware',
        'django.middleware.clickjacking.XFrameOptionsMiddleware',
        
        # Custom middleware (comment if causing issues)
        'reminders.middleware.WorkoutReminderMiddleware',
    ]

    # Security settings for production
    if not DEBUG:
        SECURE_HSTS_SECONDS = 3600
        SECURE_HSTS_INCLUDE_SUBDOMAINS = True
        SECURE_SSL_REDIRECT = True
        SESSION_COOKIE_SECURE = True
        CSRF_COOKIE_SECURE = True
        SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

    ROOT_URLCONF = 'FitTrack.urls'

    TEMPLATES = [
        {
            'BACKEND': 'django.template.backends.django.DjangoTemplates',
            'DIRS': [BASE_DIR / "templates"],
            'APP_DIRS': True,
            'OPTIONS': {
                'context_processors': [
                    'django.template.context_processors.request',
                    'django.contrib.auth.context_processors.auth',
                    'django.contrib.messages.context_processors.messages',
                ],
            },
        },
    ]

    WSGI_APPLICATION = 'FitTrack.wsgi.application'

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
    STATIC_URL = '/static/'
    STATIC_ROOT = BASE_DIR / 'staticfiles'
    STATICFILES_DIRS = [
        BASE_DIR / 'static',
    ]

    # WhiteNoise configuration
    STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
    WHITENOISE_MANIFEST_STRICT = False  # Important for production

    # Create staticfiles directory if not exists
    if not os.path.exists(STATIC_ROOT):
        os.makedirs(STATIC_ROOT)

    # Default primary key field type
    DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

    # Custom user model
    AUTH_USER_MODEL = 'users.CustomUser'

    # Logging configuration
    LOGGING = {
        'version': 1,
        'disable_existing_loggers': False,
        'handlers': {
            'console': {
                'class': 'logging.StreamHandler',
            },
        },
        'root': {
            'handlers': ['console'],
            'level': 'DEBUG' if DEBUG else 'INFO',
        },
    }

    # Authentication URLs
    LOGIN_REDIRECT_URL = "home"
    LOGOUT_REDIRECT_URL = "home"

    # Crispy Forms
    CRISPY_ALLOWED_TEMPLATE_PACKS = "bootstrap5"
    CRISPY_TEMPLATE_PACK = "bootstrap5"

    # Email Configuration
    if DEBUG:
        EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
        logger.info("Using console email backend for development")
    else:
        EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
        EMAIL_HOST = os.getenv('SMTP_HOST', 'smtp.gmail.com')
        EMAIL_PORT = int(os.getenv('SMTP_PORT', 587))
        EMAIL_USE_TLS = os.getenv('SMTP_USE_TLS', 'True') == 'True'
        EMAIL_HOST_USER = os.getenv('SMTP_USER')
        EMAIL_HOST_PASSWORD = os.getenv('SMTP_PASSWORD')
        DEFAULT_FROM_EMAIL = os.getenv('SMTP_FROM_EMAIL', 'fittrackappication@gmail.com')
        logger.info(f"Configured SMTP with host: {EMAIL_HOST}")
    
    # Impostazioni reset password
    PASSWORD_RESET_TIMEOUT = 86400  # 24 ore in secondi
    PASSWORD_RESET_EMAIL_TEMPLATE = 'registration/password_reset_email.html'
except Exception as e:
    logger.critical(f"❌ Critical error loading settings: {str(e)}", exc_info=True)
    raise
