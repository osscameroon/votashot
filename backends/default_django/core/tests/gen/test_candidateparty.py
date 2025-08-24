from common_bases.base_testing import GenericViewSetTestCaseMixin
from core.models import CandidateParty
from core.serializers import CandidatePartySerializer
from rest_framework.test import APITestCase


class GeneratedCandidatePartyTestCase(
    APITestCase, GenericViewSetTestCaseMixin
):

    model = CandidateParty
    serializer_class = CandidatePartySerializer
    viewset_basename = "candidatepartys"
