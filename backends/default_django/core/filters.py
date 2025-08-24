from .gen.filters import (
    GeneratedCandidatePartyFilterSet,
    GeneratedPollOfficeFilterSet,
    GeneratedSourceFilterSet,
    GeneratedSourceTokenFilterSet,
    GeneratedVoteAcceptedFilterSet,
    GeneratedVoteFilterSet,
    GeneratedVoteProposedFilterSet,
    GeneratedVoterFilterSet,
    GeneratedVoteVerifiedFilterSet,
    GeneratedVotingPaperResultFilterSet,
    GeneratedVotingPaperResultProposedFilterSet,
)


class SourceFilterSet(GeneratedSourceFilterSet):

    pass


class PollOfficeFilterSet(GeneratedPollOfficeFilterSet):

    pass


class VoteFilterSet(GeneratedVoteFilterSet):

    pass


class VoteProposedFilterSet(GeneratedVoteProposedFilterSet):

    pass


class VoterFilterSet(GeneratedVoterFilterSet):

    pass


class VoteVerifiedFilterSet(GeneratedVoteVerifiedFilterSet):

    pass


class VoteAcceptedFilterSet(GeneratedVoteAcceptedFilterSet):

    pass


class CandidatePartyFilterSet(GeneratedCandidatePartyFilterSet):

    pass


class VotingPaperResultFilterSet(GeneratedVotingPaperResultFilterSet):

    pass


class VotingPaperResultProposedFilterSet(
    GeneratedVotingPaperResultProposedFilterSet
):

    pass


class SourceTokenFilterSet(GeneratedSourceTokenFilterSet):

    pass
