from .gen.base_settings import *
from decouple import config

INSTALLED_APPS.remove("pro_auth")
# INSTALLED_APPS.remove("uni_ps")
INSTALLED_APPS.remove("crispy_forms")
INSTALLED_APPS.remove("crispy_bootstrap5")

# UFRECS mode
WORK_MODE = "test"

# configure wasabi s3
DEFAULT_FILE_STORAGE = "core.storage_backends.MediaStorage"

AWS_ACCESS_KEY_ID = config("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = config("AWS_SECRET_ACCESS_KEY")
AWS_STORAGE_BUCKET_NAME = config("AWS_STORAGE_BUCKET_NAME")
AWS_S3_ENDPOINT_URL = config("AWS_S3_ENDPOINT_URL")
AWS_QUERYSTRING_EXPIRE = 3600 * 24 * 90
AWS_QUERYSTRING_AUTH = False

STS_ROLE_ARN = None
