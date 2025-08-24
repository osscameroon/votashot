from django.contrib import admin

from .gen.admin import (
    GeneratedCandidatePartyAdmin,
    GeneratedPollOfficeAdmin,
    GeneratedSourceAdmin,
    GeneratedSourceTokenAdmin,
    GeneratedVoteAcceptedAdmin,
    GeneratedVoteAdmin,
    GeneratedVoteProposedAdmin,
    GeneratedVoterAdmin,
    GeneratedVoteVerifiedAdmin,
    GeneratedVotingPaperResultAdmin,
    GeneratedVotingPaperResultProposedAdmin,
)
from .models import (
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


@admin.register(Source)
class SourceAdmin(GeneratedSourceAdmin):

    pass


@admin.register(PollOffice)
class PollOfficeAdmin(GeneratedPollOfficeAdmin):

    pass


@admin.register(Vote)
class VoteAdmin(GeneratedVoteAdmin):

    pass


@admin.register(VoteProposed)
class VoteProposedAdmin(GeneratedVoteProposedAdmin):

    pass


@admin.register(Voter)
class VoterAdmin(GeneratedVoterAdmin):

    pass


@admin.register(VoteVerified)
class VoteVerifiedAdmin(GeneratedVoteVerifiedAdmin):

    pass


@admin.register(VoteAccepted)
class VoteAcceptedAdmin(GeneratedVoteAcceptedAdmin):

    pass


@admin.register(CandidateParty)
class CandidatePartyAdmin(GeneratedCandidatePartyAdmin):

    pass


@admin.register(VotingPaperResult)
class VotingPaperResultAdmin(GeneratedVotingPaperResultAdmin):

    pass


@admin.register(VotingPaperResultProposed)
class VotingPaperResultProposedAdmin(GeneratedVotingPaperResultProposedAdmin):

    pass


@admin.register(SourceToken)
class SourceTokenAdmin(GeneratedSourceTokenAdmin):

    pass
