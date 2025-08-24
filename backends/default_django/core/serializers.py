from rest_framework.fields import BooleanField, CharField, IntegerField, ChoiceField, JSONField
from rest_framework.serializers import Serializer

from .enums import Gender, Age
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
    genre = ChoiceField(choices=Gender.choices())
    age = ChoiceField(choices=Age.choices())
    has_torn = BooleanField(default=False)


class VoteResponseSerializer(Serializer):
    id = IntegerField()
    index = IntegerField()


class VotingPaperResultInputSerializer(Serializer):
    index = IntegerField()
    paper_id = CharField()


class VotingPaperResultResponseSerializer(Serializer):
    status = CharField(default="ok")
