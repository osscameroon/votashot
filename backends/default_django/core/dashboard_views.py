from .gen.dashboard_views import (
    GeneratedCandidatePartyDashboardViewSet,
    GeneratedPollOfficeDashboardViewSet,
    GeneratedSourceDashboardViewSet,
    GeneratedVoteAcceptedDashboardViewSet,
    GeneratedVoteDashboardViewSet,
    GeneratedVoteProposedDashboardViewSet,
    GeneratedVoterDashboardViewSet,
    GeneratedVoteVerifiedDashboardViewSet,
    GeneratedVotingPaperResultDashboardViewSet,
    GeneratedVotingPaperResultProposedDashboardViewSet,
)


class SourceDashboardViewSet(GeneratedSourceDashboardViewSet):

    pass


class PollOfficeDashboardViewSet(GeneratedPollOfficeDashboardViewSet):

    pass


class VoteDashboardViewSet(GeneratedVoteDashboardViewSet):

    pass


class VoteProposedDashboardViewSet(GeneratedVoteProposedDashboardViewSet):

    pass


class VoterDashboardViewSet(GeneratedVoterDashboardViewSet):

    pass


class VoteVerifiedDashboardViewSet(GeneratedVoteVerifiedDashboardViewSet):

    pass


class VoteAcceptedDashboardViewSet(GeneratedVoteAcceptedDashboardViewSet):

    pass


class CandidatePartyDashboardViewSet(GeneratedCandidatePartyDashboardViewSet):

    pass


class VotingPaperResultDashboardViewSet(
    GeneratedVotingPaperResultDashboardViewSet
):

    pass


class VotingPaperResultProposedDashboardViewSet(
    GeneratedVotingPaperResultProposedDashboardViewSet
):

    pass


class SourceTokenDashboardViewSet(GeneratedSourceTokenDashboardViewSet):

    pass
