from common_bases.base_testing import GenericViewSetTestCaseMixin
from core.models import PollOffice
from core.serializers import PollOfficeSerializer
from rest_framework.test import APITestCase


class GeneratedPollOfficeTestCase(APITestCase, GenericViewSetTestCaseMixin):

    model = PollOffice
    serializer_class = PollOfficeSerializer
    viewset_basename = "polloffices"
