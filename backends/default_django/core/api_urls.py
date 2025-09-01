from django.urls import path

from rest_framework.routers import DefaultRouter
from .api_views import (AuthenticateApiView, ModeApiView, PollOfficeViewSet,
                        VoteApiView, VotingPaperResultView,
                        CandidatePartyViewSet, PollOfficeStatsView,
                        PollOfficeResultsView)

router = DefaultRouter()

router.register("polloffices", PollOfficeViewSet, basename="polloffices")
router.register("candidateparties", CandidatePartyViewSet, basename="candidateparties")

urlpatterns = router.urls

urlpatterns += [
    path("authenticate/", AuthenticateApiView.as_view(), name="authenticate"),
    path("mode/", ModeApiView.as_view(), name="work-mode"),
    path("vote/", VoteApiView.as_view(), name="vote"),
    path("votingpaperresult/", VotingPaperResultView.as_view(), name="voting-paper-result"),
    path("pollofficestats/", PollOfficeStatsView.as_view(), name="poll-office-stats"),
    path("pollofficeresults/", PollOfficeResultsView.as_view(), name="poll-office-results"),
]
