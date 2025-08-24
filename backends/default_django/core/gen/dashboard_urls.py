from common_bases.custom_viewsets import CustomGenericDashboardViewSet

from ..dashboard_views import (
    CandidatePartyDashboardViewSet,
    PollOfficeDashboardViewSet,
    SourceDashboardViewSet,
    SourceTokenDashboardViewSet,
    VoteAcceptedDashboardViewSet,
    VoteDashboardViewSet,
    VoteProposedDashboardViewSet,
    VoterDashboardViewSet,
    VoteVerifiedDashboardViewSet,
    VotingPaperResultDashboardViewSet,
    VotingPaperResultProposedDashboardViewSet,
)

router = CustomGenericDashboardViewSet.get_router()
router.register(
    SourceDashboardViewSet.url_basename,
    SourceDashboardViewSet,
    basename=SourceDashboardViewSet.url_basename,
)
router.register(
    PollOfficeDashboardViewSet.url_basename,
    PollOfficeDashboardViewSet,
    basename=PollOfficeDashboardViewSet.url_basename,
)
router.register(
    VoteDashboardViewSet.url_basename,
    VoteDashboardViewSet,
    basename=VoteDashboardViewSet.url_basename,
)
router.register(
    VoteProposedDashboardViewSet.url_basename,
    VoteProposedDashboardViewSet,
    basename=VoteProposedDashboardViewSet.url_basename,
)
router.register(
    VoterDashboardViewSet.url_basename,
    VoterDashboardViewSet,
    basename=VoterDashboardViewSet.url_basename,
)
router.register(
    VoteVerifiedDashboardViewSet.url_basename,
    VoteVerifiedDashboardViewSet,
    basename=VoteVerifiedDashboardViewSet.url_basename,
)
router.register(
    VoteAcceptedDashboardViewSet.url_basename,
    VoteAcceptedDashboardViewSet,
    basename=VoteAcceptedDashboardViewSet.url_basename,
)
router.register(
    CandidatePartyDashboardViewSet.url_basename,
    CandidatePartyDashboardViewSet,
    basename=CandidatePartyDashboardViewSet.url_basename,
)
router.register(
    VotingPaperResultDashboardViewSet.url_basename,
    VotingPaperResultDashboardViewSet,
    basename=VotingPaperResultDashboardViewSet.url_basename,
)
router.register(
    VotingPaperResultProposedDashboardViewSet.url_basename,
    VotingPaperResultProposedDashboardViewSet,
    basename=VotingPaperResultProposedDashboardViewSet.url_basename,
)
router.register(
    SourceTokenDashboardViewSet.url_basename,
    SourceTokenDashboardViewSet,
    basename=SourceTokenDashboardViewSet.url_basename,
)

urlpatterns = router.urls
