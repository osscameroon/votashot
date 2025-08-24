from common_bases.base_testing import GenericViewSetTestCaseMixin
from core.models import Source
from core.serializers import SourceSerializer
from rest_framework.test import APITestCase


class GeneratedSourceTestCase(APITestCase, GenericViewSetTestCaseMixin):

    model = Source
    serializer_class = SourceSerializer
    viewset_basename = "sources"
