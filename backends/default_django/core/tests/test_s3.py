from django.test import TestCase
from django.conf import settings
import boto3
from core.utils import issue_scoped_creds


class S3TestCase(TestCase):

    def test_issue_scoped_creds(self):
        # Issue scoped credentials for the specific poll/user prefix
        creds = issue_scoped_creds("random-poll-if", "elector-id")
        print(creds)

        # Use the scoped credentials to upload a file to the configured S3 endpoint
        s3 = boto3.client(
            "s3",
            endpoint_url=settings.AWS_S3_ENDPOINT_URL,
            region_name=settings.AWS_S3_REGION_NAME,
            aws_access_key_id=creds["AccessKeyId"],
            aws_secret_access_key=creds["SecretAccessKey"],
            aws_session_token=creds["SessionToken"],
        )

        key = "random-poll-if/elector-id/sub_again/test-file.txt"
        resp = s3.put_object(
            Bucket=settings.AWS_STORAGE_BUCKET_NAME,
            Key=key,
            Body=b"hello-from-test",
            ContentType="text/plain",
        )

        # Basic success assertion: ETag present on successful put
        self.assertIn("ETag", resp)
