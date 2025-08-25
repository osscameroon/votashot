import logging
from datetime import timedelta
from typing import Dict

from django.contrib.auth import get_user_model
from django.core.cache import cache
from rest_framework.authentication import (
    TokenAuthentication as DrfTokenAuthentication,
)
from rest_framework.authentication import get_authorization_header
from django.contrib.auth.backends import BaseBackend, ModelBackend

from core.models import SourceToken
from core.serializers import SourceTokenSerializer

from rest_framework.exceptions import AuthenticationFailed
from django.utils import timezone


User = get_user_model()
logger = logging.getLogger("api")


class TokenCache:
    cache: Dict[str, SourceToken] = {}


class TokenAuthentication(DrfTokenAuthentication):
    keyword = "Bearer"

    def authenticate(self, request, username=None, password=None, **kwargs):
        try:
            auth = get_authorization_header(request).decode()
            if not auth:
                return

            if len(auth.split()) < 2:
                return

            key = auth.split()[1]

            source_token = TokenCache.cache.get(key)
            if not source_token:
                source_token: SourceToken = SourceToken.objects.get(token=key)
                TokenCache.cache[key] = source_token
                logger.debug(f"key {key} given to user {source_token.user}")

            # if source_token and source_token.expiry:
            #     if source_token.expiry < timezone.now():
            #         TokenCache.cache.pop(key, None)
            #         raise AuthenticationFailed("The API token has expired")

            if source_token:
                request.source_token = source_token
                return source_token.user, key

        except SourceToken.DoesNotExist:
            return None
