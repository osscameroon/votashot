from common_bases.custom_mixins import (
    CustomCreateModelMixin,
    CustomDestroyModelMixin,
    CustomUpdateModelMixin,
)
from common_bases.custom_viewsets import CustomGenericViewSet
from core.filters import (
    CandidatePartyFilterSet,
    PollOfficeFilterSet,
    SourceFilterSet,
    SourceTokenFilterSet,
    VoteAcceptedFilterSet,
    VoteFilterSet,
    VoteProposedFilterSet,
    VoterFilterSet,
    VoteVerifiedFilterSet,
    VotingPaperResultFilterSet,
    VotingPaperResultProposedFilterSet,
)
from core.models import (
    CandidateParty,
    PollOffice,
    Source,
    SourceToken,
    Vote,
    VoteAccepted,
    VoteProposed,
    Voter,
    VoteVerified,
    VotingPaperResult,
    VotingPaperResultProposed,
)
from core.serializers import (
    CandidatePartySerializer,
    PollOfficeSerializer,
    SourceSerializer,
    SourceTokenSerializer,
    VoteAcceptedSerializer,
    VoteProposedSerializer,
    VoterSerializer,
    VoteSerializer,
    VoteVerifiedSerializer,
    VotingPaperResultProposedSerializer,
    VotingPaperResultSerializer,
)
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.mixins import ListModelMixin, RetrieveModelMixin
from rest_framework.permissions import AllowAny
from uni_ps.utils import PermissionAction, get_queryset_for_user

from ..services.candidateparty import CandidatePartyServices
from ..services.polloffice import PollOfficeServices
from ..services.source import SourceServices
from ..services.sourcetoken import SourceTokenServices
from ..services.vote import VoteServices
from ..services.voteaccepted import VoteAcceptedServices
from ..services.voteproposed import VoteProposedServices
from ..services.voter import VoterServices
from ..services.voteverified import VoteVerifiedServices
from ..services.votingpaperresult import VotingPaperResultServices
from ..services.votingpaperresultproposed import (
    VotingPaperResultProposedServices,
)


class GeneratedSourceViewSet(
    CustomGenericViewSet,
    CustomCreateModelMixin,
    CustomUpdateModelMixin,
    CustomDestroyModelMixin,
    ListModelMixin,
    RetrieveModelMixin,
):

    pre_services = {
        "create": SourceServices.pre_create_source,
        "update": SourceServices.pre_update_source,
        "partial_update": SourceServices.pre_partial_update_source,
        "delete": SourceServices.pre_delete_source,
    }
    post_services = {
        "create": SourceServices.post_create_source,
        "update": SourceServices.post_update_source,
        "partial_update": SourceServices.post_partial_update_source,
        "delete": SourceServices.post_delete_source,
    }
    serializer_class = SourceSerializer
    queryset = Source.objects.none()
    filter_backends = [DjangoFilterBackend]
    filterset_class = SourceFilterSet

    def get_queryset(
        self,
    ):
        """None"""
        if (
            AllowAny in self.permission_classes
            and not self.request.user.is_authenticated
        ):
            return Source.objects.all()

        if self.request.user.is_superuser:
            return Source.objects.all()

        return get_queryset_for_user(
            self.request.user, Source, PermissionAction.VIEW
        )


class GeneratedPollOfficeViewSet(
    CustomGenericViewSet,
    CustomCreateModelMixin,
    CustomUpdateModelMixin,
    CustomDestroyModelMixin,
    ListModelMixin,
    RetrieveModelMixin,
):

    pre_services = {
        "create": PollOfficeServices.pre_create_polloffice,
        "update": PollOfficeServices.pre_update_polloffice,
        "partial_update": PollOfficeServices.pre_partial_update_polloffice,
        "delete": PollOfficeServices.pre_delete_polloffice,
    }
    post_services = {
        "create": PollOfficeServices.post_create_polloffice,
        "update": PollOfficeServices.post_update_polloffice,
        "partial_update": PollOfficeServices.post_partial_update_polloffice,
        "delete": PollOfficeServices.post_delete_polloffice,
    }
    serializer_class = PollOfficeSerializer
    queryset = PollOffice.objects.none()
    filter_backends = [DjangoFilterBackend]
    filterset_class = PollOfficeFilterSet

    def get_queryset(
        self,
    ):
        """None"""
        if (
            AllowAny in self.permission_classes
            and not self.request.user.is_authenticated
        ):
            return PollOffice.objects.all()

        if self.request.user.is_superuser:
            return PollOffice.objects.all()

        return get_queryset_for_user(
            self.request.user, PollOffice, PermissionAction.VIEW
        )


class GeneratedVoteViewSet(
    CustomGenericViewSet,
    CustomCreateModelMixin,
    CustomUpdateModelMixin,
    CustomDestroyModelMixin,
    ListModelMixin,
    RetrieveModelMixin,
):

    pre_services = {
        "create": VoteServices.pre_create_vote,
        "update": VoteServices.pre_update_vote,
        "partial_update": VoteServices.pre_partial_update_vote,
        "delete": VoteServices.pre_delete_vote,
    }
    post_services = {
        "create": VoteServices.post_create_vote,
        "update": VoteServices.post_update_vote,
        "partial_update": VoteServices.post_partial_update_vote,
        "delete": VoteServices.post_delete_vote,
    }
    serializer_class = VoteSerializer
    queryset = Vote.objects.none()
    filter_backends = [DjangoFilterBackend]
    filterset_class = VoteFilterSet

    def get_queryset(
        self,
    ):
        """None"""
        if (
            AllowAny in self.permission_classes
            and not self.request.user.is_authenticated
        ):
            return Vote.objects.all()

        if self.request.user.is_superuser:
            return Vote.objects.all()

        return get_queryset_for_user(
            self.request.user, Vote, PermissionAction.VIEW
        )


class GeneratedVoteProposedViewSet(
    CustomGenericViewSet,
    CustomCreateModelMixin,
    CustomUpdateModelMixin,
    CustomDestroyModelMixin,
    ListModelMixin,
    RetrieveModelMixin,
):

    pre_services = {
        "create": VoteProposedServices.pre_create_voteproposed,
        "update": VoteProposedServices.pre_update_voteproposed,
        "partial_update": VoteProposedServices.pre_partial_update_voteproposed,
        "delete": VoteProposedServices.pre_delete_voteproposed,
    }
    post_services = {
        "create": VoteProposedServices.post_create_voteproposed,
        "update": VoteProposedServices.post_update_voteproposed,
        "partial_update": VoteProposedServices.post_partial_update_voteproposed,
        "delete": VoteProposedServices.post_delete_voteproposed,
    }
    serializer_class = VoteProposedSerializer
    queryset = VoteProposed.objects.none()
    filter_backends = [DjangoFilterBackend]
    filterset_class = VoteProposedFilterSet

    def get_queryset(
        self,
    ):
        """None"""
        if (
            AllowAny in self.permission_classes
            and not self.request.user.is_authenticated
        ):
            return VoteProposed.objects.all()

        if self.request.user.is_superuser:
            return VoteProposed.objects.all()

        return get_queryset_for_user(
            self.request.user, VoteProposed, PermissionAction.VIEW
        )


class GeneratedVoterViewSet(
    CustomGenericViewSet,
    CustomCreateModelMixin,
    CustomUpdateModelMixin,
    CustomDestroyModelMixin,
    ListModelMixin,
    RetrieveModelMixin,
):

    pre_services = {
        "create": VoterServices.pre_create_voter,
        "update": VoterServices.pre_update_voter,
        "partial_update": VoterServices.pre_partial_update_voter,
        "delete": VoterServices.pre_delete_voter,
    }
    post_services = {
        "create": VoterServices.post_create_voter,
        "update": VoterServices.post_update_voter,
        "partial_update": VoterServices.post_partial_update_voter,
        "delete": VoterServices.post_delete_voter,
    }
    serializer_class = VoterSerializer
    queryset = Voter.objects.none()
    filter_backends = [DjangoFilterBackend]
    filterset_class = VoterFilterSet

    def get_queryset(
        self,
    ):
        """None"""
        if (
            AllowAny in self.permission_classes
            and not self.request.user.is_authenticated
        ):
            return Voter.objects.all()

        if self.request.user.is_superuser:
            return Voter.objects.all()

        return get_queryset_for_user(
            self.request.user, Voter, PermissionAction.VIEW
        )


class GeneratedVoteVerifiedViewSet(
    CustomGenericViewSet,
    CustomCreateModelMixin,
    CustomUpdateModelMixin,
    CustomDestroyModelMixin,
    ListModelMixin,
    RetrieveModelMixin,
):

    pre_services = {
        "create": VoteVerifiedServices.pre_create_voteverified,
        "update": VoteVerifiedServices.pre_update_voteverified,
        "partial_update": VoteVerifiedServices.pre_partial_update_voteverified,
        "delete": VoteVerifiedServices.pre_delete_voteverified,
    }
    post_services = {
        "create": VoteVerifiedServices.post_create_voteverified,
        "update": VoteVerifiedServices.post_update_voteverified,
        "partial_update": VoteVerifiedServices.post_partial_update_voteverified,
        "delete": VoteVerifiedServices.post_delete_voteverified,
    }
    serializer_class = VoteVerifiedSerializer
    queryset = VoteVerified.objects.none()
    filter_backends = [DjangoFilterBackend]
    filterset_class = VoteVerifiedFilterSet

    def get_queryset(
        self,
    ):
        """None"""
        if (
            AllowAny in self.permission_classes
            and not self.request.user.is_authenticated
        ):
            return VoteVerified.objects.all()

        if self.request.user.is_superuser:
            return VoteVerified.objects.all()

        return get_queryset_for_user(
            self.request.user, VoteVerified, PermissionAction.VIEW
        )


class GeneratedVoteAcceptedViewSet(
    CustomGenericViewSet,
    CustomCreateModelMixin,
    CustomUpdateModelMixin,
    CustomDestroyModelMixin,
    ListModelMixin,
    RetrieveModelMixin,
):

    pre_services = {
        "create": VoteAcceptedServices.pre_create_voteaccepted,
        "update": VoteAcceptedServices.pre_update_voteaccepted,
        "partial_update": VoteAcceptedServices.pre_partial_update_voteaccepted,
        "delete": VoteAcceptedServices.pre_delete_voteaccepted,
    }
    post_services = {
        "create": VoteAcceptedServices.post_create_voteaccepted,
        "update": VoteAcceptedServices.post_update_voteaccepted,
        "partial_update": VoteAcceptedServices.post_partial_update_voteaccepted,
        "delete": VoteAcceptedServices.post_delete_voteaccepted,
    }
    serializer_class = VoteAcceptedSerializer
    queryset = VoteAccepted.objects.none()
    filter_backends = [DjangoFilterBackend]
    filterset_class = VoteAcceptedFilterSet

    def get_queryset(
        self,
    ):
        """None"""
        if (
            AllowAny in self.permission_classes
            and not self.request.user.is_authenticated
        ):
            return VoteAccepted.objects.all()

        if self.request.user.is_superuser:
            return VoteAccepted.objects.all()

        return get_queryset_for_user(
            self.request.user, VoteAccepted, PermissionAction.VIEW
        )


class GeneratedCandidatePartyViewSet(
    CustomGenericViewSet,
    CustomCreateModelMixin,
    CustomUpdateModelMixin,
    CustomDestroyModelMixin,
    ListModelMixin,
    RetrieveModelMixin,
):

    pre_services = {
        "create": CandidatePartyServices.pre_create_candidateparty,
        "update": CandidatePartyServices.pre_update_candidateparty,
        "partial_update": CandidatePartyServices.pre_partial_update_candidateparty,
        "delete": CandidatePartyServices.pre_delete_candidateparty,
    }
    post_services = {
        "create": CandidatePartyServices.post_create_candidateparty,
        "update": CandidatePartyServices.post_update_candidateparty,
        "partial_update": CandidatePartyServices.post_partial_update_candidateparty,
        "delete": CandidatePartyServices.post_delete_candidateparty,
    }
    serializer_class = CandidatePartySerializer
    queryset = CandidateParty.objects.none()
    filter_backends = [DjangoFilterBackend]
    filterset_class = CandidatePartyFilterSet

    def get_queryset(
        self,
    ):
        """None"""
        if (
            AllowAny in self.permission_classes
            and not self.request.user.is_authenticated
        ):
            return CandidateParty.objects.all()

        if self.request.user.is_superuser:
            return CandidateParty.objects.all()

        return get_queryset_for_user(
            self.request.user, CandidateParty, PermissionAction.VIEW
        )


class GeneratedVotingPaperResultViewSet(
    CustomGenericViewSet,
    CustomCreateModelMixin,
    CustomUpdateModelMixin,
    CustomDestroyModelMixin,
    ListModelMixin,
    RetrieveModelMixin,
):

    pre_services = {
        "create": VotingPaperResultServices.pre_create_votingpaperresult,
        "update": VotingPaperResultServices.pre_update_votingpaperresult,
        "partial_update": VotingPaperResultServices.pre_partial_update_votingpaperresult,
        "delete": VotingPaperResultServices.pre_delete_votingpaperresult,
    }
    post_services = {
        "create": VotingPaperResultServices.post_create_votingpaperresult,
        "update": VotingPaperResultServices.post_update_votingpaperresult,
        "partial_update": VotingPaperResultServices.post_partial_update_votingpaperresult,
        "delete": VotingPaperResultServices.post_delete_votingpaperresult,
    }
    serializer_class = VotingPaperResultSerializer
    queryset = VotingPaperResult.objects.none()
    filter_backends = [DjangoFilterBackend]
    filterset_class = VotingPaperResultFilterSet

    def get_queryset(
        self,
    ):
        """None"""
        if (
            AllowAny in self.permission_classes
            and not self.request.user.is_authenticated
        ):
            return VotingPaperResult.objects.all()

        if self.request.user.is_superuser:
            return VotingPaperResult.objects.all()

        return get_queryset_for_user(
            self.request.user, VotingPaperResult, PermissionAction.VIEW
        )


class GeneratedVotingPaperResultProposedViewSet(
    CustomGenericViewSet,
    CustomCreateModelMixin,
    CustomUpdateModelMixin,
    CustomDestroyModelMixin,
    ListModelMixin,
    RetrieveModelMixin,
):

    pre_services = {
        "create": VotingPaperResultProposedServices.pre_create_votingpaperresultproposed,
        "update": VotingPaperResultProposedServices.pre_update_votingpaperresultproposed,
        "partial_update": VotingPaperResultProposedServices.pre_partial_update_votingpaperresultproposed,
        "delete": VotingPaperResultProposedServices.pre_delete_votingpaperresultproposed,
    }
    post_services = {
        "create": VotingPaperResultProposedServices.post_create_votingpaperresultproposed,
        "update": VotingPaperResultProposedServices.post_update_votingpaperresultproposed,
        "partial_update": VotingPaperResultProposedServices.post_partial_update_votingpaperresultproposed,
        "delete": VotingPaperResultProposedServices.post_delete_votingpaperresultproposed,
    }
    serializer_class = VotingPaperResultProposedSerializer
    queryset = VotingPaperResultProposed.objects.none()
    filter_backends = [DjangoFilterBackend]
    filterset_class = VotingPaperResultProposedFilterSet

    def get_queryset(
        self,
    ):
        """None"""
        if (
            AllowAny in self.permission_classes
            and not self.request.user.is_authenticated
        ):
            return VotingPaperResultProposed.objects.all()

        if self.request.user.is_superuser:
            return VotingPaperResultProposed.objects.all()

        return get_queryset_for_user(
            self.request.user, VotingPaperResultProposed, PermissionAction.VIEW
        )


class GeneratedSourceTokenViewSet(
    CustomGenericViewSet,
    CustomCreateModelMixin,
    CustomUpdateModelMixin,
    CustomDestroyModelMixin,
    ListModelMixin,
    RetrieveModelMixin,
):

    pre_services = {
        "create": SourceTokenServices.pre_create_sourcetoken,
        "update": SourceTokenServices.pre_update_sourcetoken,
        "partial_update": SourceTokenServices.pre_partial_update_sourcetoken,
        "delete": SourceTokenServices.pre_delete_sourcetoken,
    }
    post_services = {
        "create": SourceTokenServices.post_create_sourcetoken,
        "update": SourceTokenServices.post_update_sourcetoken,
        "partial_update": SourceTokenServices.post_partial_update_sourcetoken,
        "delete": SourceTokenServices.post_delete_sourcetoken,
    }
    serializer_class = SourceTokenSerializer
    queryset = SourceToken.objects.none()
    filter_backends = [DjangoFilterBackend]
    filterset_class = SourceTokenFilterSet

    def get_queryset(
        self,
    ):
        """None"""
        if (
            AllowAny in self.permission_classes
            and not self.request.user.is_authenticated
        ):
            return SourceToken.objects.all()

        if self.request.user.is_superuser:
            return SourceToken.objects.all()

        return get_queryset_for_user(
            self.request.user, SourceToken, PermissionAction.VIEW
        )
