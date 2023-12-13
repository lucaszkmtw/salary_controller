import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

SECRET_KEY = os.getenv('SECRET_KEY')
LOGLEVEL = os.getenv('DJANGO_LOGLEVEL', 'debug').upper()

BASE_DIR = Path(__file__).resolve().parent.parent.parent

SESSION_COOKIE_AGE = 30 * 60
SESSION_EXPIRE_AFTER_LAST_ACTIVITY = True
SESSION_EXPIRE_SECONDS = 60 * 60  # Luego de 1 horas de inactividad desloguea al Usuario
SESSION_ENGINE = 'django.contrib.sessions.backends.cache'


# Admin Charts
ADMIN_CHARTS_NVD3_JS_PATH = 'admin_charts/nv.d3.js'
ADMIN_CHARTS_NVD3_CSS_PATH = 'admin_charts/nv.d3.css'
ADMIN_CHARTS_D3_JS_PATH = 'admin_charts/d3.v3.min.js'

INSTALLED_APPS = [
    # Django
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Extensions
    'django_select2',
    'adminsortable2',
    'widget_tweaks',
    'rangefilter',  # Admin date range filter


    # Django REST Framework
    'rest_framework',
    'rest_framework_datatables',

    # Celery
    'celery',
    'django_celery_beat',
    'django_celery_results',

    # My Apps
    'aumentos',
    'cuadricula',
    'django_rest_framework',
    'hiscar',
    'main',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django_session_timeout.middleware.SessionTimeoutMiddleware',

    # Loginrequired in all views
    'main.middleware.LoginRequiredMiddleware'
]


TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': ['%s/templates/' % (BASE_DIR), os.path.join(BASE_DIR, 'templates'), ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
            'libraries':{
                'tags': 'templates.template_tags.tags',
            }
        },
    },
]

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'postgres',
        'USER': 'postgres',
        'PASSWORD': 'postgres',
        'HOST': os.getenv('POSTGRES_HOST'),
        'PORT': '5432',
    }
}

if os.environ.get('GITHUB_WORKFLOW'):
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': 'postgres',
            'USER': 'postgres',
            'PASSWORD': 'postgres',
            'HOST': '127.0.0.1',
            'PORT': '5432',
        }
    }

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

ROOT_URLCONF = 'project.urls'

WSGI_APPLICATION = 'project.wsgi.application'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

LANGUAGE_CODE = 'es-AR'

TIME_ZONE = 'America/Buenos_Aires'

USE_I18N = True

USE_L10N = False

USE_TZ = True

STATIC_URL = '/static/'
STATICFILES_DIRS = (
    os.path.join(BASE_DIR, 'static'),
)
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/accounts/login'

REDIS_HOST = os.getenv('REDIS_HOST')
CELERY_BROKER_URL = f'redis://{REDIS_HOST}:6379'
CELERY_RESULT_BACKEND = 'django-db'

CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.redis.RedisCache",
        "LOCATION": CELERY_BROKER_URL,
        "KEY_PREFIX": "cache-siliq"
    },
    "select2": {
        "BACKEND": "django.core.cache.backends.redis.RedisCache",
        "LOCATION": CELERY_BROKER_URL,
    }
}

SELECT2_CACHE_BACKEND = "select2"

FIXTURE_DIRS = (
    os.path.join(BASE_DIR, 'fixtures'),
)

REST_FRAMEWORK = {
    'DEFAULT_RENDERER_CLASSES': (
        'rest_framework.renderers.JSONRenderer',
        'rest_framework.renderers.BrowsableAPIRenderer',
        'rest_framework_datatables.renderers.DatatablesRenderer',
    ),
    'DEFAULT_FILTER_BACKENDS': (
        'rest_framework_datatables.filters.DatatablesFilterBackend',
    ),
    'DEFAULT_PAGINATION_CLASS': 'rest_framework_datatables.pagination.DatatablesPageNumberPagination',
    'PAGE_SIZE': 50,
}
