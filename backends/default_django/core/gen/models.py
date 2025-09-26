from datetime import datetime
from typing import Optional, Union

from core.enums import Age, Gender, SourceType
from django.db import models


class GeneratedSource(models.Model):

    elector_id: Union[str, models.CharField] = models.CharField(
        max_length=255,
    )
    password: Union[str, models.CharField] = models.CharField(
        max_length=255,
    )
    type: Union[str, models.CharField] = models.CharField(
        max_length=255,
        choices=SourceType.choices(),
    )
    official_org: Optional[Union[str, models.CharField]] = models.CharField(
        max_length=255,
        null=True,
        blank=True,
    )
    full_name: Optional[Union[str, models.CharField]] = models.CharField(
        max_length=255,
        null=True,
        blank=True,
    )
    email: Optional[Union[str, models.CharField]] = models.CharField(
        max_length=255,
        null=True,
        blank=True,
    )
    phone_number: Optional[Union[str, models.CharField]] = models.CharField(
        max_length=255,
        null=True,
        blank=True,
    )
    created_at: Union[datetime, models.DateTimeField] = models.DateTimeField(
        auto_now_add=True,
    )

    class Meta:

        abstract = True


class GeneratedPollOffice(models.Model):

    name: Union[str, models.CharField] = models.CharField(
        max_length=255,
    )
    identifier: Union[str, models.CharField] = models.CharField(
        max_length=255,
    )
    country: Union[str, models.CharField] = models.CharField(
        max_length=255,
    )
    state: Optional[Union[str, models.CharField]] = models.CharField(
        max_length=255,
        null=True,
        blank=True,
    )
    region: Optional[Union[str, models.CharField]] = models.CharField(
        max_length=255,
        null=True,
        blank=True,
    )
    city: Optional[Union[str, models.CharField]] = models.CharField(
        max_length=255,
        null=True,
        blank=True,
    )
    county: Optional[Union[str, models.CharField]] = models.CharField(
        max_length=255,
        null=True,
        blank=True,
    )
    district: Optional[Union[str, models.CharField]] = models.CharField(
        max_length=255,
        null=True,
        blank=True,
    )
    created_at: Union[datetime, models.DateTimeField] = models.DateTimeField(
        auto_now_add=True,
    )
    voters_count: Optional[Union[int, models.IntegerField]] = (
        models.IntegerField(
            null=True,
            blank=True,
        )
    )

    class Meta:

        abstract = True


class GeneratedVote(models.Model):

    index: Union[int, models.IntegerField] = models.IntegerField()
    created_at: Union[datetime, models.DateTimeField] = models.DateTimeField(
        auto_now_add=True,
    )
    poll_office: Union["PollOffice", models.ForeignKey["PollOffice"]] = (
        models.ForeignKey(
            "core.PollOffice",
            models.DO_NOTHING,
            related_name="votes",
        )
    )

    class Meta:

        abstract = True


class GeneratedVoteProposed(models.Model):

    gender: Union[str, models.CharField] = models.CharField(
        max_length=255,
        choices=Gender.choices(),
    )
    age: Union[str, models.CharField] = models.CharField(
        max_length=255,
        choices=Age.choices(),
    )
    has_torn: Union[bool, models.BooleanField] = models.BooleanField(
        default=False
    )
    created_at: Union[datetime, models.DateTimeField] = models.DateTimeField(
        auto_now_add=True,
    )
    source: Union["Source", models.ForeignKey["Source"]] = models.ForeignKey(
        "core.Source",
        models.DO_NOTHING,
        related_name="proposed_votes",
    )
    vote: Union["Vote", models.ForeignKey["Vote"]] = models.ForeignKey(
        "core.Vote",
        models.DO_NOTHING,
        related_name="proposed_votes",
    )

    class Meta:

        abstract = True


class GeneratedVoter(models.Model):

    elector_id: Union[str, models.CharField] = models.CharField(
        max_length=255,
    )
    full_name: Optional[Union[str, models.CharField]] = models.CharField(
        max_length=255,
        null=True,
        blank=True,
    )
    created_at: Union[datetime, models.DateTimeField] = models.DateTimeField(
        auto_now_add=True,
    )

    class Meta:

        abstract = True


class GeneratedVoteVerified(models.Model):

    gender: Union[str, models.CharField] = models.CharField(
        max_length=255,
        choices=Gender.choices(),
    )
    age: Union[str, models.CharField] = models.CharField(
        max_length=255,
        choices=Age.choices(),
    )
    has_torn: Union[bool, models.BooleanField] = models.BooleanField(
        default=False
    )
    created_at: Union[datetime, models.DateTimeField] = models.DateTimeField(
        auto_now_add=True,
    )
    voter: "Voter" = models.OneToOneField(
        "core.Voter",
        models.DO_NOTHING,
    )
    vote: "Vote" = models.OneToOneField(
        "core.Vote",
        models.DO_NOTHING,
    )

    class Meta:

        abstract = True


class GeneratedVoteAccepted(models.Model):

    gender: Union[str, models.CharField] = models.CharField(
        max_length=255,
        choices=Gender.choices(),
    )
    age: Union[str, models.CharField] = models.CharField(
        max_length=255,
        choices=Age.choices(),
    )
    has_torn: Union[bool, models.BooleanField] = models.BooleanField(
        default=False
    )
    created_at: Union[datetime, models.DateTimeField] = models.DateTimeField(
        auto_now_add=True,
    )
    vote: "Vote" = models.OneToOneField(
        "core.Vote",
        models.DO_NOTHING,
    )

    class Meta:

        abstract = True


class GeneratedCandidateParty(models.Model):

    party_name: Union[str, models.CharField] = models.CharField(
        max_length=255,
    )
    candidate_name: Union[str, models.CharField] = models.CharField(
        max_length=255,
    )
    identifier: Union[str, models.CharField] = models.CharField(
        max_length=255,
    )
    created_at: Union[datetime, models.DateTimeField] = models.DateTimeField(
        auto_now_add=True,
    )

    class Meta:

        abstract = True


class GeneratedVotingPaperResult(models.Model):

    index: Union[int, models.IntegerField] = models.IntegerField()
    created_at: Union[datetime, models.DateTimeField] = models.DateTimeField(
        auto_now_add=True,
    )
    poll_office: Union["PollOffice", models.ForeignKey["PollOffice"]] = (
        models.ForeignKey(
            "core.PollOffice",
            models.DO_NOTHING,
            related_name="vp_results",
        )
    )
    accepted_candidate_party: Optional[
        Union["CandidateParty", models.ForeignKey["CandidateParty"]]
    ] = models.ForeignKey(
        "core.CandidateParty",
        models.DO_NOTHING,
        related_name="vp_results",
        null=True,
        blank=True,
    )

    class Meta:

        abstract = True


class GeneratedVotingPaperResultProposed(models.Model):

    created_at: Union[datetime, models.DateTimeField] = models.DateTimeField(
        auto_now_add=True,
    )
    source: Union["Source", models.ForeignKey["Source"]] = models.ForeignKey(
        "core.Source",
        models.DO_NOTHING,
        related_name="proposed_vp_results",
    )
    vp_result: Union[
        "VotingPaperResult", models.ForeignKey["VotingPaperResult"]
    ] = models.ForeignKey(
        "core.VotingPaperResult",
        models.DO_NOTHING,
        related_name="proposed_vp_results",
    )
    party_candidate: Union[
        "CandidateParty", models.ForeignKey["CandidateParty"]
    ] = models.ForeignKey(
        "core.CandidateParty",
        models.DO_NOTHING,
        related_name="proposed_in_vp_results",
    )

    class Meta:

        abstract = True


class GeneratedSourceToken(models.Model):

    token: Union[str, models.CharField] = models.CharField(
        max_length=255,
        unique=True,
    )
    s3_credentials: Optional[Union[list, dict, models.JSONField]] = (
        models.JSONField(
            null=True,
            blank=True,
        )
    )
    created_at: Union[datetime, models.DateTimeField] = models.DateTimeField(
        auto_now_add=True,
    )
    poll_office: Union["PollOffice", models.ForeignKey["PollOffice"]] = (
        models.ForeignKey(
            "core.PollOffice",
            models.DO_NOTHING,
            related_name="source_tokens",
        )
    )
    source: Union["Source", models.ForeignKey["Source"]] = models.ForeignKey(
        "core.Source",
        models.DO_NOTHING,
        related_name="source_tokens",
    )

    class Meta:

        abstract = True
