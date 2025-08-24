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
from rest_framework.fields import BooleanField, CharField, IntegerField
from rest_framework.serializers import ModelSerializer


class GeneratedSourceSerializer(ModelSerializer):

    class Meta:

        model = Source
        fields = [
            "id",
            "elector_id",
            "password",
            "type",
            "official_org",
            "full_name",
            "email",
            "phone_number",
            "created_at",
        ]


class GeneratedPollOfficeSerializer(ModelSerializer):

    class Meta:

        model = PollOffice
        fields = [
            "id",
            "name",
            "identifier",
            "country",
            "state",
            "region",
            "city",
            "county",
            "district",
            "created_at",
        ]


class GeneratedVoteSerializer(ModelSerializer):

    poll_office_id = IntegerField(required=True)

    class Meta:

        model = Vote
        fields = ["id", "index", "created_at", "poll_office_id"]


class GeneratedVoteProposedSerializer(ModelSerializer):

    source_id = IntegerField(required=True)
    vote_id = IntegerField(required=True)

    class Meta:

        model = VoteProposed
        fields = [
            "id",
            "gender",
            "age",
            "has_torn",
            "created_at",
            "source_id",
            "vote_id",
        ]


class GeneratedVoterSerializer(ModelSerializer):

    class Meta:

        model = Voter
        fields = ["id", "elector_id", "full_name", "created_at"]


class GeneratedVoteVerifiedSerializer(ModelSerializer):

    voter_id = IntegerField(required=True)
    vote_id = IntegerField(required=True)

    class Meta:

        model = VoteVerified
        fields = [
            "id",
            "gender",
            "age",
            "has_torn",
            "created_at",
            "voter_id",
            "vote_id",
        ]


class GeneratedVoteAcceptedSerializer(ModelSerializer):

    vote_id = IntegerField(required=True)

    class Meta:

        model = VoteAccepted
        fields = ["id", "gender", "age", "has_torn", "created_at", "vote_id"]


class GeneratedCandidatePartySerializer(ModelSerializer):

    class Meta:

        model = CandidateParty
        fields = [
            "id",
            "party_name",
            "candidate_name",
            "identifier",
            "created_at",
        ]


class GeneratedVotingPaperResultSerializer(ModelSerializer):

    poll_office_id = IntegerField(required=True)
    accepted_candidate_party_id = IntegerField(required=True)

    class Meta:

        model = VotingPaperResult
        fields = [
            "id",
            "index",
            "created_at",
            "poll_office_id",
            "accepted_candidate_party_id",
        ]


class GeneratedVotingPaperResultProposedSerializer(ModelSerializer):

    source_id = IntegerField(required=True)
    vp_result_id = IntegerField(required=True)
    party_candidate_id = IntegerField(required=True)

    class Meta:

        model = VotingPaperResultProposed
        fields = [
            "id",
            "created_at",
            "source_id",
            "vp_result_id",
            "party_candidate_id",
        ]


class GeneratedSourceTokenSerializer(ModelSerializer):

    poll_office_id = IntegerField(required=True)
    source_id = IntegerField(required=True)

    class Meta:

        model = SourceToken
        fields = [
            "id",
            "token",
            "s3_credentials",
            "created_at",
            "poll_office_id",
            "source_id",
        ]
