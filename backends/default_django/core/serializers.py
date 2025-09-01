from django.db import transaction
from rest_framework.fields import (
    BooleanField,
    CharField,
    ChoiceField,
    IntegerField,
    JSONField, FloatField,
)
from rest_framework.serializers import Serializer

from .enums import Age, Gender
from .gen.serializers import (
    GeneratedCandidatePartySerializer,
    GeneratedPollOfficeSerializer,
    GeneratedSourceSerializer,
    GeneratedSourceTokenSerializer,
    GeneratedVoteAcceptedSerializer,
    GeneratedVoteProposedSerializer,
    GeneratedVoterSerializer,
    GeneratedVoteSerializer,
    GeneratedVoteVerifiedSerializer,
    GeneratedVotingPaperResultProposedSerializer,
    GeneratedVotingPaperResultSerializer,
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


class SourceSerializer(GeneratedSourceSerializer):

    class Meta:

        model = Source
        fields = GeneratedSourceSerializer.Meta.fields + []


class PollOfficeSerializer(GeneratedPollOfficeSerializer):

    class Meta:

        model = PollOffice
        fields = GeneratedPollOfficeSerializer.Meta.fields + []


class VoteSerializer(GeneratedVoteSerializer):

    class Meta:

        model = Vote
        fields = GeneratedVoteSerializer.Meta.fields + []


class VoteProposedSerializer(GeneratedVoteProposedSerializer):

    class Meta:

        model = VoteProposed
        fields = GeneratedVoteProposedSerializer.Meta.fields + []


class VoterSerializer(GeneratedVoterSerializer):

    class Meta:

        model = Voter
        fields = GeneratedVoterSerializer.Meta.fields + []


class VoteVerifiedSerializer(GeneratedVoteVerifiedSerializer):

    class Meta:

        model = VoteVerified
        fields = GeneratedVoteVerifiedSerializer.Meta.fields + []


class VoteAcceptedSerializer(GeneratedVoteAcceptedSerializer):

    class Meta:

        model = VoteAccepted
        fields = GeneratedVoteAcceptedSerializer.Meta.fields + []


class CandidatePartySerializer(GeneratedCandidatePartySerializer):

    class Meta:

        model = CandidateParty
        fields = GeneratedCandidatePartySerializer.Meta.fields + []


class VotingPaperResultSerializer(GeneratedVotingPaperResultSerializer):

    class Meta:

        model = VotingPaperResult
        fields = GeneratedVotingPaperResultSerializer.Meta.fields + []


class VotingPaperResultProposedSerializer(
    GeneratedVotingPaperResultProposedSerializer
):

    class Meta:

        model = VotingPaperResultProposed
        fields = GeneratedVotingPaperResultProposedSerializer.Meta.fields + []


class AuthenticationInputSerializer(Serializer):
    elector_id = CharField()
    password = CharField(required=False, allow_blank=True, allow_null=True)
    poll_office_id = CharField()


class AuthenticationResponseSerializer(Serializer):
    token = CharField()
    poll_office_id = CharField()
    s3 = JSONField()


class SourceTokenSerializer(GeneratedSourceTokenSerializer):

    class Meta:

        model = SourceToken
        fields = GeneratedSourceTokenSerializer.Meta.fields + []


class VoteInputSerializer(Serializer):
    index = IntegerField()
    gender = ChoiceField(choices=Gender.choices())
    age = ChoiceField(choices=Age.choices())
    has_torn = BooleanField(default=False)

    def save(self, **kwargs):
        request = self.context.get("request")
        source_token: SourceToken = request.source_token
        poll_office_id = source_token.poll_office_id

        with transaction.atomic():
            poll_office = PollOffice.objects.select_for_update().get(
                pk=poll_office_id
            )
            vote, created = Vote.objects.get_or_create(
                poll_office=poll_office, index=self.validated_data["index"]
            )
            vote_proposed: VoteProposed = VoteProposed.objects.filter(
                vote=vote, source=source_token.source
            ).first()
            if not vote_proposed:
                vote_proposed = VoteProposed.objects.create(
                    vote=vote,
                    source=source_token.source,
                    gender=self.validated_data.get("gender"),
                    age=self.validated_data.get("age"),
                    has_torn=self.validated_data.get("has_torn", False),
                )
            else:
                vote_proposed.gender = self.validated_data.get("gender")
                vote_proposed.age = self.validated_data.get("age")
                vote_proposed.has_torn = self.validated_data.get(
                    "has_torn", False
                )
                vote_proposed.save()

        return vote_proposed


class VoteResponseSerializer(Serializer):
    id = IntegerField()
    index = IntegerField()


class VotingPaperResultInputSerializer(Serializer):
    index = IntegerField()
    party_id = CharField()

    def save(self, **kwargs):
        request = self.context.get("request")
        source_token: SourceToken = request.source_token
        poll_office_id = source_token.poll_office_id

        with transaction.atomic():
            poll_office = PollOffice.objects.select_for_update().get(
                pk=poll_office_id
            )
            voting_paper_result, created = (
                VotingPaperResult.objects.get_or_create(
                    poll_office=poll_office, index=self.validated_data["index"]
                )
            )
            vp_result_proposed: VotingPaperResultProposed = (
                VotingPaperResultProposed.objects.filter(
                    vp_result=voting_paper_result, source=source_token.source
                ).first()
            )
            candidate_party = CandidateParty.objects.get(
                identifier=self.validated_data["party_id"]
            )
            vp_result_proposed = (
                VotingPaperResultProposed.objects.get_or_create(
                    vp_result=voting_paper_result,
                    source=source_token.source,
                    defaults={"party_candidate": candidate_party},
                )
            )

        return vp_result_proposed


class VotingPaperResultResponseSerializer(Serializer):
    status = CharField(default="ok")


class PollOfficeStatTotalsPartSerializer(Serializer):
    votes = IntegerField()
    male = IntegerField()
    female = IntegerField()
    less_30 = IntegerField()
    less_60 = IntegerField()
    more_60 = IntegerField()
    has_torn = IntegerField()


class PollOfficeStatLastVotePartSerializer(Serializer):
    index = IntegerField()
    gender = CharField()
    age = CharField()
    has_torn = IntegerField()


class PollOfficeStatsSerializer(Serializer):
    totals = PollOfficeStatTotalsPartSerializer()
    last_vote = PollOfficeStatLastVotePartSerializer()


class PollOfficeResultLastPaperPartSerializer(Serializer):
    index = IntegerField()
    party_id = CharField()


class PollOfficeResultResultPartSerializer(Serializer):
    party_id = CharField()
    ballots = IntegerField()
    share = FloatField()


class PollOfficeResultSerializer(Serializer):
    last_paper = PollOfficeResultLastPaperPartSerializer(allow_null=True)
    results = PollOfficeResultResultPartSerializer(many=True)
    total_ballots = IntegerField()
