from core.enums import Age, Gender
from core.models import PollOffice, Source, Vote, VoteProposed
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

# Keep generated viewset tests
from .gen.test_vote import GeneratedVoteTestCase


class VoteTestCase(GeneratedVoteTestCase):
    pass


class VoteApiViewTests(APITestCase):
    def setUp(self):
        # Minimal PollOffice that authentication and voting flows depend on
        self.poll_office_identifier = "PO-TEST-API-001"
        self.poll_office = PollOffice.objects.create(
            name="Test Office",
            identifier=self.poll_office_identifier,
            country="FR",
            city="Paris",
        )

        self.auth_url = reverse("authenticate")
        self.vote_url = reverse("vote")

    def create_token(self, elector_id: str, password: str = "pass") -> str:
        # Acquire a SourceToken via the public authentication endpoint (no mocking)
        payload = {
            "elector_id": elector_id,
            "password": password,
            "poll_office_id": self.poll_office_identifier,
        }
        resp = self.client.post(self.auth_url, data=payload, format="json")
        self.assertEqual(resp.status_code, status.HTTP_200_OK, msg=resp.data)
        return resp.data["token"]

    def auth_headers(self, token: str) -> dict:
        return {"HTTP_AUTHORIZATION": f"Bearer {token}"}

    def test_requires_authentication(self):
        # No Authorization header -> IsAuthenticated should reject
        resp = self.client.post(self.vote_url, data={}, format="json")
        self.assertEqual(resp.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_invalid_payload_returns_400_with_error_details(self):
        token = self.create_token("01-02-003-0004-05-000100")
        # Missing required fields triggers serializer errors
        resp = self.client.post(
            self.vote_url, data={}, format="json", **self.auth_headers(token)
        )
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(resp.data.get("code"), "invalid_data")
        self.assertIn("errors", resp.data)

    def test_first_submission_creates_vote_and_voteproposed(self):
        elector_id = "02-12-069-0080-16-000700"
        token = self.create_token(elector_id)
        payload = {
            "index": 1,
            "gender": Gender.MALE,
            "age": Age.LESS_30,
            "has_torn": False,
        }

        resp = self.client.post(
            self.vote_url,
            data=payload,
            format="json",
            **self.auth_headers(token),
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK, msg=resp.data)
        self.assertIn("id", resp.data)
        self.assertEqual(resp.data.get("index"), payload["index"])  # echo back

        # DB: a Source exists and exactly one VoteProposed linked to its Vote
        src = Source.objects.get(elector_id=elector_id)
        vp = VoteProposed.objects.get(
            pk=resp.data["id"]
        )  # the returned id is VoteProposed.pk
        self.assertEqual(vp.source_id, src.id)
        self.assertEqual(vp.gender, payload["gender"])
        self.assertEqual(vp.age, payload["age"])
        self.assertEqual(vp.has_torn, payload["has_torn"])

        # A Vote for this PollOffice must exist
        self.assertEqual(
            Vote.objects.filter(poll_office=self.poll_office).count(), 1
        )
        self.assertEqual(vp.vote.poll_office_id, self.poll_office.id)

    def test_second_submission_updates_voteproposed_not_duplicate(self):
        elector_id = "02-12-069-0080-16-000701"
        token = self.create_token(elector_id)

        first = {
            "index": 9,
            "gender": Gender.FEMALE,
            "age": Age.LESS_60,
            "has_torn": False,
        }
        r1 = self.client.post(
            self.vote_url,
            data=first,
            format="json",
            **self.auth_headers(token),
        )
        self.assertEqual(r1.status_code, status.HTTP_200_OK, msg=r1.data)
        first_id = r1.data["id"]

        # Change attributes; same Source + PollOffice should update existing VoteProposed
        second = {
            "index": 9,  # same index
            "gender": Gender.MALE,
            "age": Age.MORE_60,
            "has_torn": True,
        }
        r2 = self.client.post(
            self.vote_url,
            data=second,
            format="json",
            **self.auth_headers(token),
        )
        self.assertEqual(r2.status_code, status.HTTP_200_OK, msg=r2.data)
        second_id = r2.data["id"]
        self.assertEqual(
            first_id, second_id, "VoteProposed must be updated, not duplicated"
        )

        # DB assertions
        src = Source.objects.get(elector_id=elector_id)
        self.assertEqual(VoteProposed.objects.filter(source=src).count(), 1)
        vp = VoteProposed.objects.get(pk=first_id)
        self.assertEqual(vp.gender, second["gender"])  # updated
        self.assertEqual(vp.age, second["age"])  # updated
        self.assertTrue(vp.has_torn)

    def test_two_sources_share_same_vote_same_index(self):
        # Two different sources propose for same PollOffice and same index
        token_a = self.create_token("02-12-069-0080-16-000710")
        token_b = self.create_token("02-12-069-0080-16-000711")

        payload = {"index": 3, "gender": Gender.MALE, "age": Age.LESS_30}
        ra = self.client.post(
            self.vote_url,
            data=payload,
            format="json",
            **self.auth_headers(token_a),
        )
        rb = self.client.post(
            self.vote_url,
            data=payload,
            format="json",
            **self.auth_headers(token_b),
        )
        self.assertEqual(ra.status_code, status.HTTP_200_OK, msg=ra.data)
        self.assertEqual(rb.status_code, status.HTTP_200_OK, msg=rb.data)

        # DB: exactly one Vote row for the PollOffice (upsert-like behavior), two proposed votes
        votes = Vote.objects.filter(poll_office=self.poll_office)
        self.assertEqual(votes.count(), 1)
        vp_all = VoteProposed.objects.filter(vote=votes.first())
        self.assertEqual(vp_all.count(), 2)

        # Both VoteProposed link to the same Vote
        vp_ids = [ra.data["id"], rb.data["id"]]
        linked_votes = set(
            VoteProposed.objects.filter(pk__in=vp_ids).values_list(
                "vote_id", flat=True
            )
        )
        self.assertEqual(len(linked_votes), 1)

    def test_different_index_creates_distinct_votes(self):
        # Intended behavior: distinct Vote per (poll_office, index)
        token_a = self.create_token("02-12-069-0080-16-000720")
        token_b = self.create_token("02-12-069-0080-16-000721")

        pa = {"index": 10, "gender": Gender.MALE, "age": Age.LESS_30}
        pb = {"index": 11, "gender": Gender.FEMALE, "age": Age.MORE_60}

        ra = self.client.post(
            self.vote_url, data=pa, format="json", **self.auth_headers(token_a)
        )
        rb = self.client.post(
            self.vote_url, data=pb, format="json", **self.auth_headers(token_b)
        )
        self.assertEqual(ra.status_code, status.HTTP_200_OK, msg=ra.data)
        self.assertEqual(rb.status_code, status.HTTP_200_OK, msg=rb.data)

        # Expect two Vote rows for the PollOffice with the respective indices
        votes = Vote.objects.filter(poll_office=self.poll_office)
        # Note: This test encodes the intended design; current implementation may fail it.
        self.assertEqual(votes.count(), 2)
        self.assertSetEqual(
            set(votes.values_list("index", flat=True)), {10, 11}
        )

    def test_has_torn_defaults_to_false(self):
        token = self.create_token("02-12-069-0080-16-000730")
        payload = {"index": 5, "gender": Gender.FEMALE, "age": Age.LESS_60}
        resp = self.client.post(
            self.vote_url,
            data=payload,
            format="json",
            **self.auth_headers(token),
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK, msg=resp.data)
        vp = VoteProposed.objects.get(pk=resp.data["id"])
        self.assertFalse(vp.has_torn)

    def test_invalid_gender_and_age_rejected(self):
        token = self.create_token("02-12-069-0080-16-000740")
        payload = {"index": 7, "gender": "invalid", "age": "nope"}
        resp = self.client.post(
            self.vote_url,
            data=payload,
            format="json",
            **self.auth_headers(token),
        )
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(resp.data.get("code"), "invalid_data")
        self.assertIn("gender", resp.data.get("errors", {}))
        self.assertIn("age", resp.data.get("errors", {}))
