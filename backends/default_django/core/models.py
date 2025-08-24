from django.contrib.auth.models import AbstractUser
from django.db import models

from .gen.models import (
    GeneratedCandidateParty,
    GeneratedPollOffice,
    GeneratedSource,
    GeneratedSourceToken,
    GeneratedVote,
    GeneratedVoteAccepted,
    GeneratedVoteProposed,
    GeneratedVoter,
    GeneratedVoteVerified,
    GeneratedVotingPaperResult,
    GeneratedVotingPaperResultProposed,
)


class Source(GeneratedSource):

    pass


class PollOffice(GeneratedPollOffice):

    pass


class Vote(GeneratedVote):

    pass


class VoteProposed(GeneratedVoteProposed):

    pass


class Voter(GeneratedVoter):

    pass


class VoteVerified(GeneratedVoteVerified):

    pass


class VoteAccepted(GeneratedVoteAccepted):

    pass


class CandidateParty(GeneratedCandidateParty):

    pass


class VotingPaperResult(GeneratedVotingPaperResult):

    pass


class VotingPaperResultProposed(GeneratedVotingPaperResultProposed):

    pass


class User(AbstractUser):

    pass


class SourceToken(GeneratedSourceToken):

    pass
