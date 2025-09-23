from .gen.base_settings import *
from decouple import config

ALLOWED_HOSTS = ['localhost', '127.0.0.1', 'testserver', 'ufrecs.dev.osscameroon.com']

INSTALLED_APPS.remove("pro_auth")
# INSTALLED_APPS.remove("uni_ps")
INSTALLED_APPS.remove("crispy_forms")
INSTALLED_APPS.remove("common_bases")
INSTALLED_APPS.remove("crispy_bootstrap5")
INSTALLED_APPS.append('corsheaders')
INSTALLED_APPS.append('cacheops')
# UFRECS mode
WORK_MODE = "test"

# MIDDLEWARE.append("silk.middleware.SilkyMiddleware")

# configure wasabi s3
DEFAULT_FILE_STORAGE = "core.storage_backends.MediaStorage"

AWS_ACCESS_KEY_ID = config("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = config("AWS_SECRET_ACCESS_KEY")
AWS_STORAGE_BUCKET_NAME = config("AWS_STORAGE_BUCKET_NAME")
AWS_S3_ENDPOINT_URL = config("AWS_S3_ENDPOINT_URL")
AWS_QUERYSTRING_EXPIRE = 3600 * 24 * 90
AWS_QUERYSTRING_AUTH = False

STS_ROLE_ARN = None

REST_FRAMEWORK = {
    "DEFAULT_RENDERER_CLASSES": ("rest_framework.renderers.JSONRenderer",),
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "core.authentication.TokenAuthentication",
        "rest_framework.authentication.SessionAuthentication"
    ),
    "DEFAULT_PERMISSION_CLASSES": ("rest_framework.permissions.IsAuthenticated",),
    # "DEFAULT_THROTTLE_CLASSES": ("rest_framework.throttling.ScopedRateThrottle",),
    # "DEFAULT_THROTTLE_RATES": {"subscription": "100/hour"},
    # "EXCEPTION_HANDLER": "apps.api.exceptions.custom_exception_handler",
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.LimitOffsetPagination",
    "PAGE_SIZE": 100,
    "TEST_REQUEST_DEFAULT_FORMAT": "json",
    "DEFAULT_FILTER_BACKENDS": ["django_filters.rest_framework.DjangoFilterBackend"],
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
}

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': config("DB_NAME"),
        'USER': config("DB_USER"),
        'PASSWORD': config("DB_PASSWORD"),
        'HOST': 'localhost',
        'PORT': config("DB_PORT"),
    }
}

# CORS configuration
CORS_ALLOW_ALL_ORIGINS = True

CACHEOPS_REDIS = {
    'host': 'localhost', # redis-server is on same machine
    'port': 6379,        # default redis port
    'db': 1,             # SELECT non-default redis database
                         # using separate redis db or redis instance
                         # is highly recommended

    'socket_timeout': 3,   # connection timeout in seconds, optional
}

CACHEOPS = {
    # Automatically cache any User.objects.get() calls for 15 minutes
    # This also includes .first() and .last() calls,
    # as well as request.user or post.author access,
    # where Post.author is a foreign key to auth.User
    # 'auth.user': {'ops': 'get', 'timeout': 60*15},

    # Automatically cache all gets and queryset fetches
    # to other django.contrib.auth models for an hour
    # 'auth.*': {'ops': {'fetch', 'get'}, 'timeout': 60*60},

    # Cache all queries to Permission
    # 'all' is an alias for {'get', 'fetch', 'count', 'aggregate', 'exists'}
    # 'auth.permission': {'ops': 'all', 'timeout': 60*60},

    # Enable manual caching on all other models with default timeout of an hour
    # Use Post.objects.cache().get(...)
    #  or Tags.objects.filter(...).order_by(...).cache()
    # to cache particular ORM request.
    # Invalidation is still automatic
    '*.*': {'ops': (), 'timeout': 60*60},
}

LOGS_DIR = BASE_DIR.joinpath("logs")
try:
    LOGS_DIR.mkdir()
except Exception:
    pass

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "standard": {
            "format": "[%(asctime)s] %(levelname)s [%(name)s:%(lineno)s] %(message)s - %(pathname)s",
            "datefmt": "%d/%b/%Y %H:%M:%S",
        },
    },
    "handlers": {
        "default": {
            "level": "DEBUG",
            "class": "logging.handlers.RotatingFileHandler",
            "filename": str(LOGS_DIR / "default.log"),
            "formatter": "standard",
            "maxBytes": 104857600,
            "backupCount": 2,
        },
        "handler_error": {
            "level": "ERROR",
            "class": "logging.handlers.RotatingFileHandler",
            "filename": str(LOGS_DIR / "error.log"),
            "formatter": "standard",
            "maxBytes": 104857600,
            "backupCount": 2,
        },
        "console": {
            "level": "DEBUG",
            "class": "logging.StreamHandler",
            "formatter": "standard",
        },
    },
    "loggers": {
        "django": {
            "handlers": ["handler_error"],
            "level": "ERROR",
            "propagate": True,
        },
        "": {
            "handlers": ["default", "handler_error", "console"],
            "level": "INFO",
            "propagate": True,
        },
    },
}
