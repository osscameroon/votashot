from common_bases.base_testing import GenericViewSetTestCaseMixin
from core.models import VotingPaperResultProposed
from core.serializers import VotingPaperResultProposedSerializer
from rest_framework.test import APITestCase


class GeneratedVotingPaperResultProposedTestCase(
    APITestCase, GenericViewSetTestCaseMixin
):

    model = VotingPaperResultProposed
    serializer_class = VotingPaperResultProposedSerializer
    viewset_basename = "votingpaperresultproposeds"
