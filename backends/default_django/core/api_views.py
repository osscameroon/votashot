import json
import os
import secrets
from datetime import timedelta

import boto3
from common_bases.custom_viewsets import CustomGenericViewSet
from django.conf import settings
from django.utils import timezone
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.mixins import ListModelMixin
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .enums import SourceType
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
from .models import PollOffice, Source, SourceToken, VoteProposed
from .serializers import (
    AuthenticationInputSerializer,
    AuthenticationResponseSerializer,
    PollOfficeSerializer,
    VoteInputSerializer,
    VoteResponseSerializer,
    VotingPaperResultInputSerializer,
    VotingPaperResultResponseSerializer,
    VotingPaperResultSerializer,
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


class CandidatePartyViewSet(GeneratedCandidatePartyViewSet):

    pass


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
