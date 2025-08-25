from django.contrib.auth.models import AbstractUser
from django.contrib.auth.hashers import make_password, check_password as django_check_password
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
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    pass


class Source(GeneratedSource):

    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.pk:
            self.user = self.user or User.objects.create_user(username=self.elector_id)
        return super().save(*args, **kwargs)

    def set_password(self, password):
        # Mirror Django's set_password behavior, hashing and syncing linked User
        hashed = make_password(password)
        self.password = hashed

    def check_password(self, password):
        # Validate the given raw password against the stored hash
        if not self.password:
            return False
        return django_check_password(password, self.password)


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


class SourceToken(GeneratedSourceToken):

    pass
