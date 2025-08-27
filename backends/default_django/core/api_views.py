import json
import os
import secrets
from datetime import timedelta

import boto3
from django.db.models.aggregates import Count
from django.db.models.query_utils import Q

from common_bases.custom_viewsets import CustomGenericViewSet
from django.conf import settings
from django.utils import timezone
from drf_spectacular.utils import extend_schema, OpenApiParameter
from rest_framework import status
from rest_framework.mixins import ListModelMixin
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .enums import SourceType, Gender, Age
from .gen.api_views import (
    GeneratedCandidatePartyViewSet,
    GeneratedPollOfficeViewSet,
    GeneratedSourceTokenViewSet,
    GeneratedSourceViewSet,
    GeneratedVoteAcceptedViewSet,
    GeneratedVoteProposedViewSet,
    GeneratedVoterViewSet,
    GeneratedVoteVerifiedViewSet,
    GeneratedVoteViewSet,
    GeneratedVotingPaperResultProposedViewSet,
    GeneratedVotingPaperResultViewSet,
)
from .models import PollOffice, Source, SourceToken, VoteProposed, Vote, VoteAccepted, VotingPaperResult, CandidateParty
from .serializers import (
    AuthenticationInputSerializer,
    AuthenticationResponseSerializer,
    PollOfficeSerializer,
    VoteInputSerializer,
    VoteResponseSerializer,
    VotingPaperResultInputSerializer,
    VotingPaperResultResponseSerializer,
    VotingPaperResultSerializer, PollOfficeStatsSerializer, VoteProposedSerializer, VoteAcceptedSerializer,
    PollOfficeResultSerializer, CandidatePartySerializer,
)

STS_ROLE_ARN = settings.STS_ROLE_ARN
sts = boto3.client("sts")
# Defaults used when running without AWS STS
REGION = os.getenv("AWS_REGION", "us-east-1")
base_path = getattr(settings, "AWS_S3_ENDPOINT_URL", "")


class SourceViewSet(GeneratedSourceViewSet):

    pass


class PollOfficeViewSet(CustomGenericViewSet, ListModelMixin):

    queryset = PollOffice.objects.all()
    serializer_class = PollOfficeSerializer
    permission_classes = [AllowAny]


class VoteViewSet(GeneratedVoteViewSet):

    pass


class VoteProposedViewSet(GeneratedVoteProposedViewSet):

    pass


class VoterViewSet(GeneratedVoterViewSet):

    pass


class VoteVerifiedViewSet(GeneratedVoteVerifiedViewSet):

    pass


class VoteAcceptedViewSet(GeneratedVoteAcceptedViewSet):

    pass


class CandidatePartyViewSet(CustomGenericViewSet, ListModelMixin):

    serializer_class = CandidatePartySerializer
    permission_classes = [AllowAny]
    queryset = CandidateParty.objects.all()


class VotingPaperResultViewSet(GeneratedVotingPaperResultViewSet):

    pass


class VotingPaperResultProposedViewSet(
    GeneratedVotingPaperResultProposedViewSet
):

    pass


class ModeApiView(APIView):
    def get(self, request, *args, **kwargs):
        return Response({"mode": settings.WORK_MODE})


class AuthenticateApiView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        request=AuthenticationInputSerializer(),
        responses={200: AuthenticationResponseSerializer()},
    )
    def post(self, request, *args, **kwargs):
        seria = AuthenticationInputSerializer(data=request.data)
        if not seria.is_valid():
            return Response(
                {
                    "message": "Authentication failed",
                    "code": "auth_failed",
                    "errors": seria.errors,
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        elector_id = seria.validated_data["elector_id"]
        poll_office_id = seria.validated_data["poll_office_id"]
        password = seria.validated_data.get("password")

        poll_office: PollOffice = PollOffice.objects.filter(
            identifier=poll_office_id
        ).first()
        if not poll_office:
            return Response(
                {
                    "message": "Authentication failed",
                    "code": "auth_failed",
                    "errors": seria.errors,
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Ensure a Source exists for this elector_id. If not, create as UNVERIFIED.
        source, created = Source.objects.get_or_create(
            elector_id=elector_id,
            defaults={"type": SourceType.UNVERIFIED},
        )
        if not created:
            source: Source
            if password:
                if source.check_password(password):
                    pass
                else:
                    return Response(
                        {
                            "message": "Authentication failed",
                            "code": "auth_failed",
                            "errors": [],
                        },
                        status=status.HTTP_400_BAD_REQUEST,
                    )
            else:
                return Response(
                    {
                        "message": "Authentication failed",
                        "code": "auth_failed",
                        "errors": [],
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

        source_token: SourceToken = SourceToken.objects.filter(
            source=source, poll_office=poll_office
        ).first()
        if not source_token:
            source_token = SourceToken.objects.create(
                source=source,
                poll_office=poll_office,
                token=secrets.token_urlsafe(32),
            )

        # In a real implementation, these would be STS credentials; fallback if STS is not configured
        if STS_ROLE_ARN:
            res = sts.assume_role(
                RoleArn=STS_ROLE_ARN,
                RoleSessionName=f"u-{elector_id}",
                DurationSeconds=3600,
                Tags=[{"Key": "user_id", "Value": elector_id}],
                TransitiveTagKeys=["user_id"],
                Policy=json.dumps(
                    {
                        "Version": "2012-10-17",
                        "Statement": [
                            {
                                "Effect": "Allow",
                                "Action": [
                                    "s3:PutObject",
                                    "s3:AbortMultipartUpload",
                                    "s3:ListMultipartUploadParts",
                                ],
                                "Resource": f"arn:aws:s3:::{settings.AWS_STORAGE_BUCKET_NAME}/{poll_office_id}/{elector_id}/*",
                            }
                        ],
                    }
                ),
            )
            c = res["Credentials"]
        else:
            c = {
                "AccessKeyId": secrets.token_urlsafe(8),
                "SecretAccessKey": secrets.token_urlsafe(16),
                "SessionToken": secrets.token_urlsafe(24),
                "Expiration": timezone.now() + timedelta(hours=1),
            }

        return Response(
            {
                "token": source_token.token,
                "poll_office_id": str(poll_office_id),
                "s3": {
                    "base_path": base_path,
                    "credentials": {
                        "bucket": settings.AWS_STORAGE_BUCKET_NAME,
                        "region": REGION,
                        "prefix": f"{poll_office_id}/{elector_id}/",
                        "accessKeyId": c["AccessKeyId"],
                        "secretAccessKey": c["SecretAccessKey"],
                        "sessionToken": c["SessionToken"],
                        "expiration": c["Expiration"],
                    },
                },
            }
        )


class SourceTokenViewSet(GeneratedSourceTokenViewSet):

    pass


class VoteApiView(APIView):

    @extend_schema(
        request=VoteInputSerializer(),
        responses=VoteResponseSerializer(),
    )
    def post(self, request, *args, **kwargs):
        seria = VoteInputSerializer(
            data=request.data, context={"request": request}
        )
        if not seria.is_valid():
            return Response(
                {
                    "message": "Invalid data",
                    "code": "invalid_data",
                    "errors": seria.errors,
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        vote_proposed: VoteProposed = seria.save()
        return Response(
            {"id": vote_proposed.pk, "index": seria.validated_data["index"]}
        )


class VotingPaperResultView(APIView):
    @extend_schema(
        request=VotingPaperResultInputSerializer(),
        responses={200: VotingPaperResultResponseSerializer()},
    )
    def post(self, request, *args, **kwargs):
        seria = VotingPaperResultInputSerializer(
            data=request.data, context={"request": request}
        )
        if not seria.is_valid():
            return Response(
                {
                    "message": "Invalid data",
                    "code": "invalid_data",
                    "errors": seria.errors,
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        seria.save()
        return Response({"status": "ok"})


class PollOfficeStatsView(APIView):
    @extend_schema(
        parameters=[
            OpenApiParameter('poll_office', type=int, required=False)
        ],
        responses={200: PollOfficeStatsSerializer()},
    )
    def get(self, request, *args, **kwargs):
        qps = getattr(request, "query_params", request.GET)
        poll_office_id = qps.get("poll_office_id") or qps.get("poll_office")
        if poll_office_id:
            return self.handle_poll_office_stats(poll_office_id)
        else:
            return self.handle_global_stats()

    def handle_global_stats(self):
        last_vote: Vote = Vote.objects.filter(voteaccepted__isnull=False).last()
        result = {}
        if last_vote:
            result['last_vote'] = VoteAcceptedSerializer(last_vote.voteaccepted).data

        totals = VoteAccepted.objects.aggregate(
            votes=Count('pk'),
            male=Count('pk', filter=Q(gender=Gender.MALE)),
            female=Count('pk', filter=Q(gender=Gender.FEMALE)),
            less_30=Count('pk', filter=Q(age=Age.LESS_30)),
            less_60=Count('pk', filter=Q(age=Age.LESS_60)),
            more_60=Count('pk', filter=Q(age=Age.MORE_60)),
            has_torn=Count('pk', filter=Q(has_torn=True)),
        )
        result["totals"] = totals

        return Response(result)

    def handle_poll_office_stats(self, poll_office_id):
        last_vote: Vote = Vote.objects.filter(poll_office_id=poll_office_id,
                                voteaccepted__isnull=False).last()
        result = {}
        if last_vote:
            result['last_vote'] = VoteAcceptedSerializer(last_vote.voteaccepted).data

        totals = VoteAccepted.objects.filter(vote__poll_office_id=poll_office_id).aggregate(
            votes=Count('pk'),
            male=Count('pk', filter=Q(gender=Gender.MALE)),
            female=Count('pk', filter=Q(gender=Gender.FEMALE)),
            less_30=Count('pk', filter=Q(age=Age.LESS_30)),
            less_60=Count('pk', filter=Q(age=Age.LESS_60)),
            more_60=Count('pk', filter=Q(age=Age.MORE_60)),
            has_torn=Count('pk', filter=Q(has_torn=True)),
        )
        result["totals"] = totals

        return Response(result)


class PollOfficeResultsView(APIView):
    @extend_schema(
        parameters=[
            OpenApiParameter('poll_office', type=int, required=False)
        ],
        responses={200: PollOfficeResultSerializer()},
    )
    def get(self, request, *args, **kwargs):
        """Return aggregated voting paper results optionally filtered by poll office.

        Response structure:
        {
          "last_paper": { "index": 250, "party_id": "ABC" },
          "results": [
            { "party_id": "ABC", "ballots": 120, "share": 0.48 },
            { "party_id": "DEF", "ballots": 100, "share": 0.40 },
            { "party_id": "GHI", "ballots": 30,  "share": 0.12 }
          ],
          "total_ballots": 250
        }
        """

        qps = getattr(request, "query_params", request.GET)
        poll_office_id = qps.get("poll_office_id") or qps.get("poll_office")
        base_qs = VotingPaperResult.objects.filter(
            accepted_candidate_party__isnull=False
        )
        if poll_office_id:
            base_qs = base_qs.filter(poll_office_id=poll_office_id)

        total_ballots = base_qs.count()

        # Aggregate ballots per candidate party identifier
        aggregated = (
            base_qs.values("accepted_candidate_party__identifier")
            .annotate(ballots=Count("pk"))
        )
        # Build result list with shares; sort deterministically by ballots desc, then party_id asc
        results = []
        for row in aggregated:
            party_id = row["accepted_candidate_party__identifier"]
            ballots = int(row["ballots"] or 0)
            share = (ballots / total_ballots) if total_ballots else 0.0
            results.append(
                {"party_id": party_id, "ballots": ballots, "share": share}
            )
        results.sort(key=lambda r: (-r["ballots"], r["party_id"]))

        response = {"results": results, "total_ballots": total_ballots}

        last_vpr = base_qs.order_by("pk").last()
        if last_vpr:
            response["last_paper"] = {
                "index": last_vpr.index,
                "party_id": last_vpr.accepted_candidate_party.identifier,
            }
        else:
            response["last_paper"] = None
        return Response(response)

        return Response(response)
