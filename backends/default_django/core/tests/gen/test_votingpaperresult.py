from common_bases.base_testing import GenericViewSetTestCaseMixin
from core.models import VotingPaperResult
from core.serializers import VotingPaperResultSerializer
from rest_framework.test import APITestCase


class GeneratedVotingPaperResultTestCase(
    APITestCase, GenericViewSetTestCaseMixin
):

    model = VotingPaperResult
    serializer_class = VotingPaperResultSerializer
    viewset_basename = "votingpaperresults"
