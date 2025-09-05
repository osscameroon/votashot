from __future__ import annotations

from typing import Any, Dict

from django.core.management.base import BaseCommand, CommandError

from core.models import Vote, VoteAccepted
from core.utils import compute_vote_decision


class Command(BaseCommand):
    help = "Analyze a Vote: recompute decision and compare with existing VoteAccepted."

    def add_arguments(self, parser):
        parser.add_argument("pk", type=int, help="Primary key of the Vote to analyze")

    def handle(self, *args, **options):
        pk: int = options["pk"]
        verbosity: int = int(options.get("verbosity", 1))

        try:
            vote: Vote = Vote.objects.get(pk=pk)
        except Vote.DoesNotExist as e:
            raise CommandError(f"Vote with pk={pk} does not exist") from e

        accepted = getattr(vote, "voteaccepted", None)
        if accepted is None:
            self.stdout.write(self.style.WARNING("No VoteAccepted linked to this Vote."))
        else:
            self.stdout.write(
                self.style.NOTICE(
                    f"Existing VoteAccepted: gender={accepted.gender}, age={accepted.age}, has_torn={accepted.has_torn}"
                )
            )

        result, details = compute_vote_decision(vote, include_details=True)
        if result is None:
            self.stdout.write(
                self.style.WARNING(
                    "Insufficient data to decide (no proposals and no verification)."
                )
            )
            return

        gender, age, has_torn = result
        self.stdout.write(
            self.style.SUCCESS(
                f"Computed decision: gender={gender}, age={age}, has_torn={has_torn}"
            )
        )

        # Comparison
        if accepted is not None:
            diffs = []
            if accepted.gender != gender:
                diffs.append(f"gender differs: {accepted.gender} -> {gender}")
            if accepted.age != age:
                diffs.append(f"age differs: {accepted.age} -> {age}")
            if bool(accepted.has_torn) != bool(has_torn):
                diffs.append(
                    f"has_torn differs: {accepted.has_torn} -> {has_torn}"
                )
            if diffs:
                self.stdout.write(self.style.WARNING("Differences found:"))
                for d in diffs:
                    self.stdout.write(f"  - {d}")
            else:
                self.stdout.write(self.style.SUCCESS("Matches existing VoteAccepted."))

        # Explanation
        if details and verbosity >= 1:
            counts = details.get("counts", {})
            self.stdout.write(
                self.style.NOTICE(
                    f"Context: proposed={counts.get('proposed', 0)}, verified={'yes' if counts.get('verified', 0) else 'no'}"
                )
            )
            for field in ("gender", "age", "has_torn"):
                fd: Dict[str, Any] = details.get(field, {})
                weights = fd.get("weights", {})
                candidates = fd.get("candidates", [])
                chosen = fd.get("chosen")
                reason = fd.get("reason", "")
                weights_str = ", ".join(
                    f"{k}={v}" for k, v in sorted(weights.items(), key=lambda kv: str(kv[0]))
                )
                tie_info = " (tie)" if len(candidates) > 1 else ""
                self.stdout.write(
                    self.style.NOTICE(
                        f"  - {field}: weights[{weights_str}] -> {chosen}{tie_info} {reason}"
                    )
                )

