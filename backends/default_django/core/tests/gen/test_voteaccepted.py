from common_bases.base_testing import GenericViewSetTestCaseMixin
from core.models import VoteAccepted
from core.serializers import VoteAcceptedSerializer
from rest_framework.test import APITestCase


class GeneratedVoteAcceptedTestCase(APITestCase, GenericViewSetTestCaseMixin):

    model = VoteAccepted
    serializer_class = VoteAcceptedSerializer
    viewset_basename = "voteaccepteds"
