from common_bases.base_testing import GenericViewSetTestCaseMixin
from core.models import Voter
from core.serializers import VoterSerializer
from rest_framework.test import APITestCase


class GeneratedVoterTestCase(APITestCase, GenericViewSetTestCaseMixin):

    model = Voter
    serializer_class = VoterSerializer
    viewset_basename = "voters"
