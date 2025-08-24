from common_bases.base_testing import GenericViewSetTestCaseMixin
from core.models import SourceToken
from core.serializers import SourceTokenSerializer
from rest_framework.test import APITestCase


class GeneratedSourceTokenTestCase(APITestCase, GenericViewSetTestCaseMixin):

    model = SourceToken
    serializer_class = SourceTokenSerializer
    viewset_basename = "sourcetokens"
