from django.core.management.base import BaseCommand
from django.db import transaction

from core.models import VotingPaperResult, VotingPaperResultProposed


class Command(BaseCommand):
    help = (
        "Delete all VotingPaperResultProposed and VotingPaperResult records."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--yes",
            "-y",
            action="store_true",
            help="Do not prompt for confirmation; assume yes.",
        )

    def handle(self, *args, **options):
        assume_yes: bool = options.get("yes", False)

        counts_before = {
            "VotingPaperResultProposed": VotingPaperResultProposed.objects.count(),
            "VotingPaperResult": VotingPaperResult.objects.count(),
        }

        if not assume_yes:
            self.stdout.write(self.style.WARNING("You are about to delete:"))
            for model_name, cnt in counts_before.items():
                self.stdout.write(f"  - {model_name}: {cnt}")
            confirm = input("Type 'delete' to proceed: ").strip().lower()
            if confirm != "delete":
                self.stdout.write(self.style.NOTICE("Aborted."))
                return

        with transaction.atomic():
            deleted = {}
            # Delete children first to satisfy FK constraints
            deleted["VotingPaperResultProposed"], _ = (
                VotingPaperResultProposed.objects.all().delete()
            )
            deleted["VotingPaperResult"], _ = VotingPaperResult.objects.all().delete()

        self.stdout.write(self.style.SUCCESS("Deletion completed."))
        for model_name in ("VotingPaperResultProposed", "VotingPaperResult"):
            self.stdout.write(
                f"  - {model_name} deleted: {deleted.get(model_name, 0)}"
            )

