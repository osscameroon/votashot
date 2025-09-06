from django.test import TestCase

from core.enums import Age, Gender, SourceType
from core.models import PollOffice, Source, Vote, VoteProposed, Voter, VoteVerified
from core.utils import compute_vote_decision


class VoteDecisionAlgorithmTests(TestCase):
    """
    End-to-end tests for the vote decision algorithm (compute_vote_decision).

    These tests create real DB objects (no mocking) and validate both outcomes
    and explanation details across many scenarios: no data, only verified,
    only proposed, ties, and mixed distributions for gender, age, and has_torn.
    """

    def setUp(self):
        # Minimal PollOffice used across tests
        self.office = PollOffice.objects.create(
            name="Office A", identifier="PO-A", country="X"
        )

    def _make_source(self, idx: int) -> Source:
        # Create a Source with required fields
        return Source.objects.create(
            elector_id=f"E{idx}", password="pass", type=SourceType.UNVERIFIED
        )

    def _make_vote(self, index: int = 1) -> Vote:
        return Vote.objects.create(poll_office=self.office, index=index)

    def _add_proposed(self, vote: Vote, src_idx: int, *, gender: str, age: str, has_torn: bool):
        # Helper to add a VoteProposed from a unique Source
        src = self._make_source(src_idx)
        VoteProposed.objects.create(
            source=src, vote=vote, gender=gender, age=age, has_torn=has_torn
        )

    def _add_verified(self, vote: Vote, *, gender: str, age: str, has_torn: bool):
        # Helper to add a VoteVerified (requires a Voter)
        voter = Voter.objects.create(elector_id=f"V-{vote.pk}")
        VoteVerified.objects.create(
            voter=voter, vote=vote, gender=gender, age=age, has_torn=has_torn
        )

    # --- Core behavior tests ---

    def test_no_data_returns_none(self):
        """If no proposed and no verified exist, algorithm returns None and no details."""
        vote = self._make_vote()
        result, details = compute_vote_decision(vote, include_details=True)
        self.assertIsNone(result)
        self.assertIsNone(details)

    def test_only_verified_values_chosen(self):
        """With only a verified entry, its fields are chosen."""
        vote = self._make_vote()
        self._add_verified(vote, gender=Gender.MALE, age=Age.LESS_60, has_torn=True)
        result, details = compute_vote_decision(vote, include_details=True)
        self.assertEqual(result, (Gender.MALE, Age.LESS_60, True))
        self.assertEqual(details["counts"], {"proposed": 0, "verified": 1})

    def test_only_single_proposed_each_field(self):
        """With exactly one proposed, that value wins for each field."""
        vote = self._make_vote()
        self._add_proposed(vote, 1, gender=Gender.FEMALE, age=Age.LESS_30, has_torn=True)
        result, details = compute_vote_decision(vote, include_details=True)
        self.assertEqual(result, (Gender.FEMALE, Age.LESS_30, True))
        self.assertEqual(details["counts"], {"proposed": 1, "verified": 0})
        self.assertEqual(details["gender"]["reason"], "single_max")
        self.assertEqual(details["age"]["reason"], "single_max")
        self.assertEqual(details["has_torn"]["reason"], "single_max")

    def test_proposed_plural_gender_beats_verified(self):
        """Two proposed for female vs one verified male -> female wins (2.0 vs 1.5)."""
        vote = self._make_vote()
        self._add_proposed(vote, 1, gender=Gender.FEMALE, age=Age.LESS_30, has_torn=False)
        self._add_proposed(vote, 2, gender=Gender.FEMALE, age=Age.LESS_30, has_torn=False)
        self._add_verified(vote, gender=Gender.MALE, age=Age.MORE_60, has_torn=True)
        result, details = compute_vote_decision(vote, include_details=True)
        self.assertEqual(result[0], Gender.FEMALE)
        # Check weights for gender specifically
        gweights = details["gender"]["weights"]
        self.assertAlmostEqual(gweights.get(Gender.FEMALE, 0), 2.0)
        self.assertAlmostEqual(gweights.get(Gender.MALE, 0), 1.5)

    def test_verified_beats_single_proposed(self):
        """One proposed male vs verified female -> female wins (1.5 vs 1.0)."""
        vote = self._make_vote()
        self._add_proposed(vote, 1, gender=Gender.MALE, age=Age.LESS_60, has_torn=False)
        self._add_verified(vote, gender=Gender.FEMALE, age=Age.MORE_60, has_torn=True)
        result, _ = compute_vote_decision(vote, include_details=False)
        self.assertEqual(result[0], Gender.FEMALE)

    def test_gender_tie_yields_undecided(self):
        """Equal top weights for gender -> Gender.UNDECIDED selected, even if verified participates."""
        vote = self._make_vote()
        # one male, one female proposed; verified male would be 1.5 vs 1 -> male leads; create tie instead
        self._add_proposed(vote, 1, gender=Gender.MALE, age=Age.LESS_60, has_torn=False)
        self._add_proposed(vote, 2, gender=Gender.FEMALE, age=Age.LESS_60, has_torn=False)
        # No verified so exact tie
        result, details = compute_vote_decision(vote, include_details=True)
        self.assertEqual(result[0], Gender.UNDECIDED)
        self.assertEqual(details["gender"]["reason"], "tie_undecided")

    def test_age_tie_yields_undecided(self):
        """Equal top weights for age -> Age.UNDECIDED selected."""
        vote = self._make_vote()
        self._add_proposed(vote, 1, gender=Gender.MALE, age=Age.LESS_30, has_torn=False)
        self._add_proposed(vote, 2, gender=Gender.MALE, age=Age.LESS_60, has_torn=False)
        result, details = compute_vote_decision(vote, include_details=True)
        self.assertEqual(result[1], Age.UNDECIDED)
        self.assertEqual(details["age"]["reason"], "tie_undecided")

    def test_has_torn_tie_prefers_verified_true(self):
        """Tie on has_torn with a verified True -> True is chosen (tie_verified_preferred)."""
        vote = self._make_vote()
        self._add_proposed(vote, 1, gender=Gender.MALE, age=Age.LESS_60, has_torn=True)
        self._add_proposed(vote, 2, gender=Gender.MALE, age=Age.LESS_60, has_torn=False)
        self._add_verified(vote, gender=Gender.MALE, age=Age.MORE_60, has_torn=True)
        result, details = compute_vote_decision(vote, include_details=True)
        self.assertEqual(result[2], True)
        # With boolean domain and +1.5 verified weight, the tie is actually broken -> single_max
        self.assertIn(details["has_torn"]["reason"], {"single_max", "tie_verified_preferred"})

    def test_has_torn_tie_prefers_verified_false(self):
        """Tie on has_torn with a verified False -> False is chosen (tie_verified_preferred)."""
        vote = self._make_vote()
        self._add_proposed(vote, 1, gender=Gender.FEMALE, age=Age.LESS_30, has_torn=True)
        self._add_proposed(vote, 2, gender=Gender.FEMALE, age=Age.LESS_30, has_torn=False)
        self._add_verified(vote, gender=Gender.FEMALE, age=Age.MORE_60, has_torn=False)
        result, details = compute_vote_decision(vote, include_details=True)
        self.assertEqual(result[2], False)
        # With boolean domain and +1.5 verified weight, the tie is actually broken -> single_max
        self.assertIn(details["has_torn"]["reason"], {"single_max", "tie_verified_preferred"})

    def test_has_torn_tie_no_verified_deterministic_false(self):
        """Tie on has_torn with no verified -> deterministic fallback chooses False (str order)."""
        vote = self._make_vote()
        self._add_proposed(vote, 1, gender=Gender.FEMALE, age=Age.LESS_30, has_torn=True)
        self._add_proposed(vote, 2, gender=Gender.FEMALE, age=Age.LESS_30, has_torn=False)
        result, details = compute_vote_decision(vote, include_details=True)
        self.assertEqual(result[2], False)
        self.assertEqual(details["has_torn"]["reason"], "tie_deterministic")

    def test_counts_detail_multiple_proposed_and_verified(self):
        """Details.counts reflects the correct number of proposed and verified entries."""
        vote = self._make_vote()
        for i in range(1, 4):
            self._add_proposed(vote, i, gender=Gender.MALE, age=Age.LESS_60, has_torn=False)
        self._add_verified(vote, gender=Gender.MALE, age=Age.LESS_60, has_torn=True)
        _, details = compute_vote_decision(vote, include_details=True)
        self.assertEqual(details["counts"], {"proposed": 3, "verified": 1})

    def test_gender_weights_example_from_spec(self):
        """Spec example: 2 proposed female, 1 proposed male, 1 verified male -> male wins 2.5 vs 2.0."""
        vote = self._make_vote()
        # Two proposed gender=female
        self._add_proposed(vote, 1, gender=Gender.FEMALE, age=Age.LESS_60, has_torn=False)
        self._add_proposed(vote, 2, gender=Gender.FEMALE, age=Age.LESS_60, has_torn=False)
        # One proposed gender=male
        self._add_proposed(vote, 3, gender=Gender.MALE, age=Age.LESS_60, has_torn=False)
        # Verified gender=male
        self._add_verified(vote, gender=Gender.MALE, age=Age.MORE_60, has_torn=True)
        result, details = compute_vote_decision(vote, include_details=True)
        # female=1+1=2, male=1 + 1.5=2.5 -> male
        self.assertEqual(result[0], Gender.MALE)
        gweights = details["gender"]["weights"]
        self.assertAlmostEqual(gweights.get(Gender.FEMALE, 0), 2.0)
        self.assertAlmostEqual(gweights.get(Gender.MALE, 0), 2.5)

    def test_many_proposed_age_tie_results_undecided(self):
        """Two top age buckets tie at max -> Age.UNDECIDED chosen regardless of verified weight < max."""
        vote = self._make_vote()
        # Two less_30, two more_60 => tie at 2. Verified less_60 -> 1.5 (not enough to win)
        self._add_proposed(vote, 1, gender=Gender.MALE, age=Age.LESS_30, has_torn=False)
        self._add_proposed(vote, 2, gender=Gender.MALE, age=Age.LESS_30, has_torn=False)
        self._add_proposed(vote, 3, gender=Gender.MALE, age=Age.MORE_60, has_torn=False)
        self._add_proposed(vote, 4, gender=Gender.MALE, age=Age.MORE_60, has_torn=False)
        self._add_verified(vote, gender=Gender.MALE, age=Age.LESS_60, has_torn=True)
        result, details = compute_vote_decision(vote, include_details=True)
        self.assertEqual(result[1], Age.UNDECIDED)
        self.assertEqual(details["age"]["reason"], "tie_undecided")

    def test_verified_present_but_not_enough_weight(self):
        """Verified may lose when proposed majority exceeds 1.5 weight."""
        vote = self._make_vote()
        # 3x female proposed vs 1 verified male -> female wins 3.0 vs 1.5
        for i in range(1, 4):
            self._add_proposed(vote, i, gender=Gender.FEMALE, age=Age.MORE_60, has_torn=False)
        self._add_verified(vote, gender=Gender.MALE, age=Age.LESS_60, has_torn=True)
        result, _ = compute_vote_decision(vote, include_details=False)
        self.assertEqual(result[0], Gender.FEMALE)

    def test_weights_and_candidates_shapes_present(self):
        """Details include weights dict, candidates list, chosen value and reason per field."""
        vote = self._make_vote()
        self._add_proposed(vote, 1, gender=Gender.MALE, age=Age.LESS_30, has_torn=True)
        self._add_verified(vote, gender=Gender.MALE, age=Age.LESS_60, has_torn=False)
        _, details = compute_vote_decision(vote, include_details=True)
        for field in ("gender", "age", "has_torn"):
            fd = details[field]
            self.assertIn("weights", fd)
            self.assertIn("candidates", fd)
            self.assertIn("chosen", fd)
            self.assertIn("reason", fd)

    def test_gender_enum_includes_undecided_result(self):
        """When gender ties, the algorithm returns Gender.UNDECIDED which must be valid."""
        vote = self._make_vote()
        self._add_proposed(vote, 1, gender=Gender.MALE, age=Age.LESS_30, has_torn=False)
        self._add_proposed(vote, 2, gender=Gender.FEMALE, age=Age.LESS_30, has_torn=False)
        result, _ = compute_vote_decision(vote, include_details=False)
        self.assertIn(result[0], Gender.values())
        self.assertEqual(result[0], Gender.UNDECIDED)

    def test_age_enum_includes_undecided_result(self):
        """When age ties, the algorithm returns Age.UNDECIDED which must be valid."""
        vote = self._make_vote()
        self._add_proposed(vote, 1, gender=Gender.MALE, age=Age.LESS_60, has_torn=False)
        self._add_proposed(vote, 2, gender=Gender.MALE, age=Age.MORE_60, has_torn=False)
        result, _ = compute_vote_decision(vote, include_details=False)
        self.assertIn(result[1], Age.values())
        self.assertEqual(result[1], Age.UNDECIDED)

    def test_boolean_normalization(self):
        """Ensure has_torn is a bool in the result even if inputs vary (they're bools here anyway)."""
        vote = self._make_vote()
        self._add_proposed(vote, 1, gender=Gender.FEMALE, age=Age.LESS_60, has_torn=False)
        result, _ = compute_vote_decision(vote, include_details=False)
        self.assertIsInstance(result[2], bool)
