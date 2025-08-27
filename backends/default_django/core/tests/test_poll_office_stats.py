from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase, APIRequestFactory, force_authenticate

from core.api_views import PollOfficeStatsView
from core.enums import Age, Gender
from core.models import PollOffice, Vote, VoteAccepted


class PollOfficeStatsViewTests(APITestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.view = PollOfficeStatsView.as_view()
        # Any authenticated user is fine for accessing the view
        User = get_user_model()
        self.user = User.objects.create_user(username="stats-user", password="x")

    def _create_office(self, identifier: str = "PO-STAT-001") -> PollOffice:
        return PollOffice.objects.create(
            name=f"Office {identifier}",
            identifier=identifier,
            country="FR",
            city="Paris",
        )

    def _accept_vote(
        self,
        office: PollOffice,
        index: int,
        gender: str,
        age: str,
        has_torn: bool = False,
    ) -> VoteAccepted:
        v = Vote.objects.create(poll_office=office, index=index)
        return VoteAccepted.objects.create(
            vote=v, gender=gender, age=age, has_torn=has_torn
        )

    def _auth_get(self, params: dict | None = None):
        request = self.factory.get("/api/stats/", data=params or {})
        force_authenticate(request, user=self.user)
        return self.view(request)

    def test_global_stats_no_accepted_votes(self):
        resp = self._auth_get()
        self.assertEqual(resp.status_code, 200)

        data = resp.data
        # No last vote key when there are no accepted votes
        self.assertNotIn("last_vote", data)

        totals = data.get("totals", {})
        self.assertEqual(
            totals,
            {
                "votes": 0,
                "male": 0,
                "female": 0,
                "less_30": 0,
                "less_60": 0,
                "more_60": 0,
                "has_torn": 0,
            },
        )

    def test_global_stats_aggregates_counts_and_sets_last_vote(self):
        o1 = self._create_office("PO-STAT-GLB-1")
        o2 = self._create_office("PO-STAT-GLB-2")

        # Create three accepted votes across two offices
        self._accept_vote(o1, 1, Gender.MALE, Age.LESS_30, has_torn=False)
        self._accept_vote(o2, 2, Gender.FEMALE, Age.LESS_60, has_torn=True)
        last = self._accept_vote(o1, 3, Gender.MALE, Age.MORE_60, has_torn=True)

        resp = self._auth_get()
        self.assertEqual(resp.status_code, 200)
        data = resp.data

        totals = data.get("totals", {})
        self.assertEqual(totals.get("votes"), 3)
        self.assertEqual(totals.get("male"), 2)
        self.assertEqual(totals.get("female"), 1)
        self.assertEqual(totals.get("less_30"), 1)
        self.assertEqual(totals.get("less_60"), 1)
        self.assertEqual(totals.get("more_60"), 1)
        self.assertEqual(totals.get("has_torn"), 2)

        # last_vote comes from the last accepted Vote by Vote PK order
        self.assertIn("last_vote", data)
        lv = data["last_vote"]
        # We assert key fields present in GeneratedVoteAcceptedSerializer
        self.assertEqual(lv.get("gender"), Gender.MALE)
        self.assertEqual(lv.get("age"), Age.MORE_60)
        self.assertTrue(lv.get("has_torn"))
        self.assertEqual(lv.get("vote_id"), last.vote_id)

    def test_poll_office_stats_filters_per_office(self):
        o1 = self._create_office("PO-STAT-ONE")
        o2 = self._create_office("PO-STAT-TWO")

        # Office 1 has two accepted votes
        self._accept_vote(o1, 1, Gender.MALE, Age.LESS_30, has_torn=False)
        last_o1 = self._accept_vote(o1, 2, Gender.FEMALE, Age.LESS_60, has_torn=True)

        # Office 2 has one accepted vote
        self._accept_vote(o2, 1, Gender.MALE, Age.MORE_60, has_torn=True)

        # Query stats for office 1 only
        resp = self._auth_get({"poll_office": o1.id})
        self.assertEqual(resp.status_code, 200)
        data = resp.data

        totals = data.get("totals", {})
        self.assertEqual(totals.get("votes"), 2)
        self.assertEqual(totals.get("male"), 1)
        self.assertEqual(totals.get("female"), 1)
        self.assertEqual(totals.get("less_30"), 1)
        self.assertEqual(totals.get("less_60"), 1)
        self.assertEqual(totals.get("more_60"), 0)
        self.assertEqual(totals.get("has_torn"), 1)

        self.assertIn("last_vote", data)
        lv = data["last_vote"]
        self.assertEqual(lv.get("vote_id"), last_o1.vote_id)
        self.assertEqual(lv.get("gender"), last_o1.gender)
        self.assertEqual(lv.get("age"), last_o1.age)
        self.assertEqual(lv.get("has_torn"), last_o1.has_torn)

    def test_poll_office_stats_no_votes_returns_zero_totals(self):
        o1 = self._create_office("PO-STAT-EMPTY")
        # Another office has votes, but not the queried one
        o2 = self._create_office("PO-STAT-NONEMPTY")
        self._accept_vote(o2, 1, Gender.MALE, Age.LESS_30, has_torn=False)

        resp = self._auth_get({"poll_office": o1.id})
        self.assertEqual(resp.status_code, 200)
        data = resp.data
        self.assertNotIn("last_vote", data)
        self.assertEqual(
            data.get("totals"),
            {
                "votes": 0,
                "male": 0,
                "female": 0,
                "less_30": 0,
                "less_60": 0,
                "more_60": 0,
                "has_torn": 0,
            },
        )

