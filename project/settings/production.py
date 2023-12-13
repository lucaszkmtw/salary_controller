import logging.config
from .settings import *
import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration
from sentry_sdk.integrations.redis import RedisIntegration

ALLOWED_HOSTS = ['localhost', 'siliq.ips.gba.gov.ar', 'app']
DEBUG = False

# Clear prev config
LOGGING_CONFIG = None

# Get loglevel from env

logging.config.dictConfig({
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'console': {
            'format': '%(asctime)s %(levelname)s [%(name)s:%(lineno)s] %(module)s %(process)d %(thread)d %(message)s',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'console',
        },
    },
    'loggers': {
        '': {
            'level': LOGLEVEL,
            'handlers': ['console', ],
        },
    },
})

if SENTRY_MOTOR_DSN := os.getenv('SENTRY_MOTOR_DSN'):

    sentry_sdk.init(
        dsn=SENTRY_MOTOR_DSN,
        integrations=[
            DjangoIntegration(),
            RedisIntegration()
        ],
        traces_sample_rate=1.0,
        send_default_pii=True,  # Attachea el user al request
        environment=os.getenv('SENTRY_ENVIRONMENT'),
        release="v1.0.0",
    )
