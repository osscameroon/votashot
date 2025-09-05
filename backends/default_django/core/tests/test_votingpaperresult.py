from core.models import CandidateParty, PollOffice, Source
from core.tests.gen.test_votingpaperresult import (
    GeneratedVotingPaperResultTestCase,
)
from django.urls import reverse
from django.utils.text import slugify
from rest_framework import status
from rest_framework.test import APITestCase


class VotingPaperResultViewTests(APITestCase):
    def setUp(self):
        # Minimal PollOffice required to obtain a token and contextualize requests
        self.poll_office_identifier = "PO-VPR-TEST-001"
        PollOffice.objects.create(
            name="VPR Office",
            identifier=self.poll_office_identifier,
            country="FR",
            city="Lyon",
        )

        self.auth_url = reverse("authenticate")
        self.vpr_url = reverse("voting-paper-result")

        # Prepare a CandidateParty required by serializer (party_id -> identifier)
        self.party_name = "Test Movement"
        self.candidate_name = "Jane Doe"
        self.party_identifier = slugify(
            f"{self.party_name}-{self.candidate_name}"
        )
        CandidateParty.objects.create(
            party_name=self.party_name,
            candidate_name=self.candidate_name,
            identifier=self.party_identifier,
        )

    def _create_token(self, elector_id: str, password: str = "pass") -> str:
        payload = {
            "elector_id": elector_id,
            "password": password,
            "poll_office_id": self.poll_office_identifier,
        }
        resp = self.client.post(self.auth_url, data=payload, format="json")
        self.assertEqual(resp.status_code, status.HTTP_200_OK, msg=resp.data)
        return resp.data["token"]

    def _auth_headers(self, token: str) -> dict:
        return {"HTTP_AUTHORIZATION": f"Bearer {token}"}

    def test_requires_authentication(self):
        resp = self.client.post(self.vpr_url, data={}, format="json")
        self.assertEqual(resp.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_invalid_when_missing_fields(self):
        token = self._create_token("02-12-069-0080-16-100100")
        # Missing both fields
        resp = self.client.post(
            self.vpr_url, data={}, format="json", **self._auth_headers(token)
        )
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(resp.data.get("code"), "invalid_data")
        self.assertIn("errors", resp.data)
        self.assertIn("index", resp.data["errors"])  # required
        self.assertIn("party_id", resp.data["errors"])  # required

    def test_invalid_when_blank_party_id(self):
        token = self._create_token("02-12-069-0080-16-100101")
        payload = {
            "index": 1,
            "party_id": "",
        }  # blank not allowed by serializer
        resp = self.client.post(
            self.vpr_url,
            data=payload,
            format="json",
            **self._auth_headers(token),
        )
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(resp.data.get("code"), "invalid_data")
        self.assertIn("party_id", resp.data.get("errors", {}))

    def test_invalid_when_index_wrong_type(self):
        token = self._create_token("02-12-069-0080-16-100102")
        payload = {"index": "not-a-number", "party_id": self.party_identifier}
        resp = self.client.post(
            self.vpr_url,
            data=payload,
            format="json",
            **self._auth_headers(token),
        )
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(resp.data.get("code"), "invalid_data")
        self.assertIn("index", resp.data.get("errors", {}))

    def test_valid_payload_returns_ok(self):
        # Expected behavior: when serializer is valid and saved, endpoint returns {"status": "ok"}
        # Current implementation likely needs a save() in VotingPaperResultInputSerializer.
        token = self._create_token("02-12-069-0080-16-100103")
        payload = {"index": 7, "party_id": self.party_identifier}
        resp = self.client.post(
            self.vpr_url,
            data=payload,
            format="json",
            **self._auth_headers(token),
        )
        # Intentionally assert the intended contract; implementation may need updates to pass.
        self.assertEqual(
            resp.status_code,
            status.HTTP_200_OK,
            msg=getattr(resp, "data", None),
        )
        self.assertEqual(resp.data, {"status": "ok"})

    def test_multiple_valid_submissions_from_same_token(self):
        token = self._create_token("02-12-069-0080-16-100104")
        payloads = [
            {"index": 1, "party_id": self.party_identifier},
            {"index": 2, "party_id": self.party_identifier},
            {"index": 3, "party_id": self.party_identifier},
        ]

        for p in payloads:
            resp = self.client.post(
                self.vpr_url,
                data=p,
                format="json",
                **self._auth_headers(token),
            )
            self.assertEqual(
                resp.status_code,
                status.HTTP_200_OK,
                msg=getattr(resp, "data", None),
            )
            self.assertEqual(resp.data, {"status": "ok"})

        # DB was hit via authentication; ensure Source persisted for this elector_id
        src = Source.objects.get(elector_id="02-12-069-0080-16-100104")
        self.assertIsNotNone(src.pk)


class VotingPaperResultTestCase(APITestCase):

    pass
