from collections import defaultdict
from datetime import datetime, timedelta
from time import sleep
from typing import Any, Dict, Iterable, Optional

from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from core.enums import Age, Gender
from core.models import Vote, VoteAccepted
from core.utils import compute_vote_decision


Weight = float


class Command(BaseCommand):
    help = (
        "Continuously decides pending votes by creating VoteAccepted from "
        "VoteProposed (w=1) and VoteVerified (w=1.5)."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--sleep",
            type=float,
            default=2.0,
            help="Seconds to sleep between polling cycles (default: 2.0)",
        )
        parser.add_argument(
            "--batch-size",
            type=int,
            default=1000,
            help="Max votes to process per cycle (default: 100)",
        )

    def handle(self, *args, **options):
        sleep_seconds: float = options["sleep"]
        batch_size: int = options["batch_size"]
        verbosity: int = int(options.get("verbosity", 1))

        self.stdout.write(
            self.style.NOTICE(
                f"decide_votes started; polling every {sleep_seconds}s, batch={batch_size}, verbosity={verbosity}."
            )
        )

        cycle_no = 0
        try:
            while True:
                cycle_no += 1
                processed = self._process_batch(batch_size=batch_size, cycle_no=cycle_no, verbosity=verbosity)
                if processed == 0:
                    if verbosity >= 1:
                        self.stdout.write(
                            self.style.NOTICE(
                                f"Cycle {cycle_no}: no pending votes; sleeping {sleep_seconds}s"
                            )
                        )
                    sleep(sleep_seconds)
                else:
                    if verbosity >= 1:
                        self.stdout.write(self.style.NOTICE(f"Cycle {cycle_no}: processed {processed} votes"))
                    # Short pause so we can quickly pick up more work
                    sleep(0.1)
        except KeyboardInterrupt:
            self.stdout.write(self.style.WARNING("Shutting down decide_votes."))

    def _process_batch(self, *, batch_size: int, cycle_no: int, verbosity: int) -> int:
        """Process up to batch_size votes lacking a VoteAccepted.

        Uses row-level locking to avoid races if multiple workers run.
        Returns the number of VoteAccepted created.
        """
        created_count = 0
        five_min_ago = timezone.now() - timedelta(minutes=5)

        # with transaction.atomic():
        #     # Lock a slice of pending votes. skip_locked prevents blocking on locks.
        pending_votes = (
            Vote.objects
            .filter(voteaccepted__isnull=True,
                    proposed_votes__created_at__lt=five_min_ago)
            .order_by("id")[:batch_size]
        )

        votes = list(pending_votes)
        if verbosity >= 1:
            self.stdout.write(
                self.style.NOTICE(
                    f"Cycle {cycle_no}: fetched {len(votes)} pending votes to decide"
                )
            )

        # Process outside the lock to minimize transaction time; we only locked ids.
        # We'll re-check existence of VoteAccepted when creating to keep idempotent.
        for vote in votes:
            try:
                result, details = compute_vote_decision(vote, include_details=True)
            except Exception as exc:
                self.stderr.write(
                    self.style.ERROR(f"Error deciding vote id={vote.id}: {exc}")
                )
                continue

            if result is None:
                # Nothing to decide (e.g., no data). Skip gracefully.
                if verbosity >= 2:
                    self.stdout.write(
                        self.style.WARNING(
                            f"Vote id={vote.id}: no proposals or verification; skipping"
                        )
                    )
                continue

            gender, age, has_torn = result
            if verbosity >= 2 and details:
                counts = details.get("counts", {})
                self.stdout.write(
                    self.style.NOTICE(
                        f"Vote id={vote.id}: proposed={counts.get('proposed', 0)}, verified={'yes' if counts.get('verified', 0) else 'no'}"
                    )
                )

            # Create inside a short transaction with a guard check for idempotency
            with transaction.atomic():
                if VoteAccepted.objects.filter(vote_id=vote.id).exists():
                    if verbosity >= 2:
                        self.stdout.write(
                            self.style.WARNING(
                                f"Vote id={vote.id}: VoteAccepted already exists; skipping"
                            )
                        )
                    continue
                VoteAccepted.objects.create(
                    vote=vote,
                    gender=gender,
                    age=age,
                    has_torn=has_torn,
                )
                created_count += 1
                if verbosity >= 2:
                    self.stdout.write(
                        self.style.SUCCESS(
                            f"Vote id={vote.id}: created VoteAccepted(gender={gender}, age={age}, has_torn={has_torn})"
                        )
                    )
                if verbosity >= 3 and details:
                    for field in ("gender", "age", "has_torn"):
                        fd = details.get(field) or {}
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

        if created_count:
            self.stdout.write(
                self.style.SUCCESS(f"Created {created_count} VoteAccepted records.")
            )
        return created_count

    
