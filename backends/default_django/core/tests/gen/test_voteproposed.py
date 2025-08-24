from common_bases.base_testing import GenericViewSetTestCaseMixin
from core.models import VoteProposed
from core.serializers import VoteProposedSerializer
from rest_framework.test import APITestCase


class GeneratedVoteProposedTestCase(APITestCase, GenericViewSetTestCaseMixin):

    model = VoteProposed
    serializer_class = VoteProposedSerializer
    viewset_basename = "voteproposeds"
