from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from core.models import PollOffice, Source


class AuthenticateApiViewTests(APITestCase):
    def setUp(self):
        # Create a PollOffice with a known identifier for tests
        self.poll_office_identifier = "PO-TEST-001"
        PollOffice.objects.create(
            name="Test Office",
            identifier=self.poll_office_identifier,
            country="FR",
            city="Paris",
        )

        self.url = reverse("authenticate")

    def test_invalid_payload_returns_400(self):
        # Missing required fields -> serializer invalid -> 400
        resp = self.client.post(self.url, data={}, format="json")
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("code", resp.data)
        self.assertEqual(resp.data["code"], "auth_failed")

    def test_nonexistent_polloffice_returns_400(self):
        payload = {
            "elector_id": "01-02-003-0004-05-000006",
            "password": "doesntmatter",
            "poll_office_id": "UNKNOWN",
        }
        resp = self.client.post(self.url, data=payload, format="json")
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(resp.data.get("code"), "auth_failed")

    def test_existing_source_missing_password_returns_400(self):
        elector_id = "02-12-069-0080-16-000550"
        s = Source.objects.create(elector_id=elector_id, type="unverified")
        s.set_password("secret")
        s.save()

        payload = {
            "elector_id": elector_id,
            # no password provided
            "poll_office_id": self.poll_office_identifier,
        }
        resp = self.client.post(self.url, data=payload, format="json")
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(resp.data.get("code"), "auth_failed")

    def test_existing_source_wrong_password_returns_400(self):
        elector_id = "02-12-069-0080-16-000551"
        s = Source.objects.create(elector_id=elector_id, type="unverified")
        s.set_password("correct-password")
        s.save()

        payload = {
            "elector_id": elector_id,
            "password": "wrong-password",
            "poll_office_id": self.poll_office_identifier,
        }
        resp = self.client.post(self.url, data=payload, format="json")
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(resp.data.get("code"), "auth_failed")

    def test_success_path_creates_token_and_returns_credentials(self):
        payload = {
            "elector_id": "02-12-069-0080-16-000560",
            "password": "anypass",
            "poll_office_id": self.poll_office_identifier,
        }

        resp = self.client.post(self.url, data=payload, format="json")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertIn("token", resp.data)
        self.assertTrue(resp.data["token"])  # non-empty token
        self.assertEqual(resp.data["poll_office_id"], self.poll_office_identifier)
        self.assertIn("s3", resp.data)
        self.assertIn("credentials", resp.data["s3"])
        creds = resp.data["s3"]["credentials"]
        self.assertIn("bucket", creds)
        self.assertIn("prefix", creds)
        self.assertTrue(creds["prefix"].startswith(f"{self.poll_office_identifier}/"))

        # DB assertions: Source and SourceToken exist
        src = Source.objects.get(elector_id=payload["elector_id"])
        from core.models import SourceToken
        token = SourceToken.objects.get(source=src)
        self.assertTrue(token.token)
