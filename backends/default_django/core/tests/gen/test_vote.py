from common_bases.base_testing import GenericViewSetTestCaseMixin
from core.models import Vote
from core.serializers import VoteSerializer
from rest_framework.test import APITestCase


class GeneratedVoteTestCase(APITestCase, GenericViewSetTestCaseMixin):

    model = Vote
    serializer_class = VoteSerializer
    viewset_basename = "votes"
