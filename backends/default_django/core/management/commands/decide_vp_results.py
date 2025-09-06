from datetime import timedelta
from time import sleep

from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from core.models import VotingPaperResult
from core.utils import compute_voting_paper_result_decision


class Command(BaseCommand):
    help = (
        "Continuously decides pending voting paper results by choosing the accepted "
        "CandidateParty from proposals (w=1) with existing acceptance preferred on ties (w=1.5)."
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
            default=100,
            help="Max voting paper results to process per cycle (default: 100)",
        )

    def handle(self, *args, **options):
        sleep_seconds: float = options["sleep"]
        batch_size: int = options["batch_size"]
        verbosity: int = int(options.get("verbosity", 1))

        self.stdout.write(
            self.style.NOTICE(
                f"decide_vp_results started; polling every {sleep_seconds}s, batch={batch_size}, verbosity={verbosity}."
            )
        )

        cycle_no = 0
        try:
            while True:
                cycle_no += 1
                processed = self._process_batch(
                    batch_size=batch_size, cycle_no=cycle_no, verbosity=verbosity
                )
                if processed == 0:
                    if verbosity >= 1:
                        self.stdout.write(
                            self.style.NOTICE(
                                f"Cycle {cycle_no}: no pending voting paper results; sleeping {sleep_seconds}s"
                            )
                        )
                    sleep(sleep_seconds)
                else:
                    if verbosity >= 1:
                        self.stdout.write(
                            self.style.NOTICE(
                                f"Cycle {cycle_no}: processed {processed} voting paper results"
                            )
                        )
                    sleep(0.1)
        except KeyboardInterrupt:
            self.stdout.write(self.style.WARNING("Shutting down decide_vp_results."))

    def _process_batch(self, *, batch_size: int, cycle_no: int, verbosity: int) -> int:
        """Process up to batch_size VotingPaperResult lacking an accepted_candidate_party.

        Uses a small age window on proposals to avoid racing with in-flight submissions.
        Returns the number of VotingPaperResult updated with an accepted_candidate_party.
        """
        updated_count = 0
        five_min_ago = timezone.now() - timedelta(minutes=5)

        pending_qs = (
            VotingPaperResult.objects
            .filter(
                accepted_candidate_party__isnull=True,
                proposed_vp_results__created_at__lt=five_min_ago,
            )
            .order_by("id")[:batch_size]
        )

        vp_results = list(pending_qs)
        if verbosity >= 1:
            self.stdout.write(
                self.style.NOTICE(
                    f"Cycle {cycle_no}: fetched {len(vp_results)} pending voting paper results to decide"
                )
            )

        for vpr in vp_results:
            try:
                chosen_party, details = compute_voting_paper_result_decision(
                    vpr, include_details=True
                )
            except Exception as exc:
                self.stderr.write(
                    self.style.ERROR(
                        f"Error deciding VotingPaperResult id={vpr.id}: {exc}"
                    )
                )
                continue

            if chosen_party is None:
                if verbosity >= 2:
                    self.stdout.write(
                        self.style.WARNING(
                            f"VotingPaperResult id={vpr.id}: no proposals/acceptance; skipping"
                        )
                    )
                continue

            if verbosity >= 2 and details:
                counts = details.get("counts", {})
                self.stdout.write(
                    self.style.NOTICE(
                        f"VotingPaperResult id={vpr.id}: proposed={counts.get('proposed', 0)}, accepted_preexists={'yes' if counts.get('verified', 0) else 'no'}"
                    )
                )

            with transaction.atomic():
                # Idempotency: check it wasn't accepted concurrently
                fresh = (
                    VotingPaperResult.objects.select_for_update()
                    .only("id", "accepted_candidate_party_id")
                    .get(id=vpr.id)
                )
                if fresh.accepted_candidate_party_id is not None:
                    if verbosity >= 2:
                        self.stdout.write(
                            self.style.WARNING(
                                f"VotingPaperResult id={vpr.id}: already accepted; skipping"
                            )
                        )
                    continue

                fresh.accepted_candidate_party = chosen_party
                fresh.save(update_fields=["accepted_candidate_party"])
                updated_count += 1

                if verbosity >= 2:
                    self.stdout.write(
                        self.style.SUCCESS(
                            f"VotingPaperResult id={vpr.id}: accepted party={chosen_party.identifier}"
                        )
                    )
                if verbosity >= 3 and details:
                    fd = details.get("party") or {}
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
                            f"  - party: weights[{weights_str}] -> {chosen}{tie_info} {reason}"
                        )
                    )

        if updated_count:
            self.stdout.write(
                self.style.SUCCESS(
                    f"Updated {updated_count} VotingPaperResult records with accepted parties."
                )
            )
        return updated_count

