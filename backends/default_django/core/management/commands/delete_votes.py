from django.core.management.base import BaseCommand
from django.db import transaction

from core.models import Vote, VoteVerified, VoteProposed, VoteAccepted


class Command(BaseCommand):
    help = "Delete all Vote, VoteVerified, VoteProposed, and VoteAccepted records."

    def add_arguments(self, parser):
        parser.add_argument(
            "--yes",
            "-y",
            action="store_true",
            help="Do not prompt for confirmation; assume yes.",
        )

    def handle(self, *args, **options):
        assume_yes: bool = options.get("yes", False)

        # Show counts before deletion
        counts_before = {
            "VoteAccepted": VoteAccepted.objects.count(),
            "VoteVerified": VoteVerified.objects.count(),
            "VoteProposed": VoteProposed.objects.count(),
            "Vote": Vote.objects.count(),
        }

        if not assume_yes:
            self.stdout.write(self.style.WARNING("You are about to delete:"))
            for model_name, cnt in counts_before.items():
                self.stdout.write(f"  - {model_name}: {cnt}")
            confirm = input("Type 'delete' to proceed: ").strip().lower()
            if confirm != "delete":
                self.stdout.write(self.style.NOTICE("Aborted."))
                return

        # Delete in dependency-safe order (children first)
        with transaction.atomic():
            deleted = {}
            deleted["VoteAccepted"], _ = VoteAccepted.objects.all().delete()
            deleted["VoteVerified"], _ = VoteVerified.objects.all().delete()
            deleted["VoteProposed"], _ = VoteProposed.objects.all().delete()
            deleted["Vote"], _ = Vote.objects.all().delete()

        self.stdout.write(self.style.SUCCESS("Deletion completed."))
        for model_name in ("VoteAccepted", "VoteVerified", "VoteProposed", "Vote"):
            self.stdout.write(f"  - {model_name} deleted: {deleted.get(model_name, 0)}")

