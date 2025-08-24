from django.urls import path

from rest_framework.routers import DefaultRouter
from .api_views import (AuthenticateApiView, ModeApiView, PollOfficeViewSet,
                        VoteApiView, VotingPaperResultView)

router = DefaultRouter()

router.register("polloffices", PollOfficeViewSet, basename="polloffices")

urlpatterns = router.urls

urlpatterns += [
    path("authenticate/", AuthenticateApiView.as_view(), name="authenticate"),
    path("mode/", ModeApiView.as_view(), name="work-mode"),
    path("vote/", VoteApiView.as_view(), name="vote"),
    path("votingpaperresult/", VotingPaperResultView.as_view(), name="voting-paper-result"),
]
