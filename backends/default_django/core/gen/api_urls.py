from rest_framework.routers import DefaultRouter

from ..api_views import (
    CandidatePartyViewSet,
    PollOfficeViewSet,
    SourceTokenViewSet,
    SourceViewSet,
    VoteAcceptedViewSet,
    VoteProposedViewSet,
    VoterViewSet,
    VoteVerifiedViewSet,
    VoteViewSet,
    VotingPaperResultProposedViewSet,
    VotingPaperResultViewSet,
)

router = DefaultRouter()
router.register("sources", SourceViewSet, basename="sources")
router.register("polloffices", PollOfficeViewSet, basename="polloffices")
router.register("votes", VoteViewSet, basename="votes")
router.register("voteproposeds", VoteProposedViewSet, basename="voteproposeds")
router.register("voters", VoterViewSet, basename="voters")
router.register("voteverifieds", VoteVerifiedViewSet, basename="voteverifieds")
router.register("voteaccepteds", VoteAcceptedViewSet, basename="voteaccepteds")
router.register(
    "candidatepartys", CandidatePartyViewSet, basename="candidatepartys"
)
router.register(
    "votingpaperresults",
    VotingPaperResultViewSet,
    basename="votingpaperresults",
)
router.register(
    "votingpaperresultproposeds",
    VotingPaperResultProposedViewSet,
    basename="votingpaperresultproposeds",
)
router.register("sourcetokens", SourceTokenViewSet, basename="sourcetokens")

urlpatterns = router.urls
