from common_bases.base_testing import GenericViewSetTestCaseMixin
from core.models import VoteVerified
from core.serializers import VoteVerifiedSerializer
from rest_framework.test import APITestCase


class GeneratedVoteVerifiedTestCase(APITestCase, GenericViewSetTestCaseMixin):

    model = VoteVerified
    serializer_class = VoteVerifiedSerializer
    viewset_basename = "voteverifieds"
