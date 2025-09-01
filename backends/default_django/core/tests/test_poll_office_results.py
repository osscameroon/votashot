from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase, APIRequestFactory, force_authenticate

from core.api_views import PollOfficeResultsView
from core.models import PollOffice, CandidateParty, VotingPaperResult


class PollOfficeResultsViewTests(APITestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.view = PollOfficeResultsView.as_view()
        User = get_user_model()
        self.user = User.objects.create_user(username="results-user", password="x")

    def _create_office(self, identifier: str) -> PollOffice:
        return PollOffice.objects.create(
            name=f"Office {identifier}",
            identifier=identifier,
            country="FR",
            city="Paris",
        )

    def _party(self, identifier: str, name: str | None = None) -> CandidateParty:
        return CandidateParty.objects.create(
            party_name=name or identifier,
            candidate_name=name or identifier,
            identifier=identifier,
        )

    def _accept_paper(
        self, office: PollOffice, index: int, party: CandidateParty
    ) -> VotingPaperResult:
        return VotingPaperResult.objects.create(
            poll_office=office, index=index, accepted_candidate_party=party
        )

    def _auth_get(self, params: dict | None = None):
        request = self.factory.get("/api/poll-office-results/", data=params or {})
        force_authenticate(request, user=self.user)
        return self.view(request)

    def test_global_results_no_accepted_returns_empty(self):
        resp = self._auth_get()
        self.assertEqual(resp.status_code, 200)
        data = resp.data
        self.assertIsNone(data.get("last_paper"))
        self.assertEqual(data.get("results"), [])
        self.assertEqual(data.get("total_ballots"), 0)

    def test_global_results_aggregates_and_sets_last_paper(self):
        o1 = self._create_office("PO-RES-1")
        o2 = self._create_office("PO-RES-2")
        pA = self._party("ABC")
        pB = self._party("DEF")

        # Create accepted results: ABC: 3 ballots, DEF: 2 ballots
        self._accept_paper(o1, 1, pA)
        self._accept_paper(o1, 2, pA)
        self._accept_paper(o2, 1, pA)
        self._accept_paper(o2, 2, pB)
        last = self._accept_paper(o1, 3, pB)  # last paper overall

        resp = self._auth_get()
        self.assertEqual(resp.status_code, 200)
        data = resp.data

        # Total ballots
        self.assertEqual(data.get("total_ballots"), 5)

        # Results aggregated by party, ordered by ballots desc then party_id asc
        results = data.get("results")
        self.assertEqual(len(results), 2)
        self.assertEqual(results[0]["party_id"], "ABC")
        self.assertEqual(results[0]["ballots"], 3)
        self.assertAlmostEqual(results[0]["share"], 3 / 5, places=6)
        self.assertEqual(results[1]["party_id"], "DEF")
        self.assertEqual(results[1]["ballots"], 2)
        self.assertAlmostEqual(results[1]["share"], 2 / 5, places=6)

        # Last paper
        lp = data.get("last_paper")
        self.assertIsNotNone(lp)
        self.assertEqual(lp["index"], last.index)
        self.assertEqual(lp["party_id"], last.accepted_candidate_party.identifier)

    def test_per_office_filtering_and_ordering(self):
        o1 = self._create_office("PO-RES-ONE")
        o2 = self._create_office("PO-RES-TWO")
        pA = self._party("AAA")
        pB = self._party("BBB")
        pC = self._party("CCC")

        # Office 1: AAA x2, BBB x1
        self._accept_paper(o1, 1, pA)
        self._accept_paper(o1, 2, pA)
        last_o1 = self._accept_paper(o1, 3, pB)

        # Office 2: BBB x2, CCC x1 (should be ignored for o1 query)
        self._accept_paper(o2, 1, pB)
        self._accept_paper(o2, 2, pB)
        self._accept_paper(o2, 3, pC)

        resp = self._auth_get({"poll_office_id": o1.id})
        self.assertEqual(resp.status_code, 200)
        data = resp.data

        self.assertEqual(data.get("total_ballots"), 3)
        results = data.get("results")
        self.assertEqual(len(results), 2)
        # Expect AAA first with 2 ballots, then BBB with 1
        self.assertEqual(results[0]["party_id"], "AAA")
        self.assertEqual(results[0]["ballots"], 2)
        self.assertAlmostEqual(results[0]["share"], 2 / 3, places=6)
        self.assertEqual(results[1]["party_id"], "BBB")
        self.assertEqual(results[1]["ballots"], 1)
        self.assertAlmostEqual(results[1]["share"], 1 / 3, places=6)

        # Last paper is the last accepted for office 1
        lp = data.get("last_paper")
        self.assertIsNotNone(lp)
        self.assertEqual(lp["index"], last_o1.index)
        self.assertEqual(lp["party_id"], last_o1.accepted_candidate_party.identifier)

    def test_per_office_no_results(self):
        o1 = self._create_office("PO-RES-EMPTY")
        o2 = self._create_office("PO-RES-NONEMPTY")
        p = self._party("ZZZ")
        self._accept_paper(o2, 1, p)

        resp = self._auth_get({"poll_office_id": o1.id})
        self.assertEqual(resp.status_code, 200)
        data = resp.data
        self.assertIsNone(data.get("last_paper"))
        self.assertEqual(data.get("results"), [])
        self.assertEqual(data.get("total_ballots"), 0)

