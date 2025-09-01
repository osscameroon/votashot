from __future__ import annotations

import random
from typing import Optional

from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils.text import slugify
from faker import Faker

from core.models import CandidateParty


def fake_party_name(fake: Faker) -> str:
    base = fake.city() if hasattr(fake, "city") else fake.word()
    suffix = random.choice(["Party", "Movement", "Alliance", "Front", "Union"])  # nosec - deterministic list
    return f"{base} {suffix}"


class Command(BaseCommand):
    help = "Create fake CandidateParty entries using Faker. The 'identifier' is a slug of party_name and candidate_name."

    def add_arguments(self, parser):
        parser.add_argument(
            "--count",
            type=int,
            default=10,
            help="Number of CandidateParty records to create (default: 10)",
        )
        parser.add_argument(
            "--locale",
            type=str,
            default=None,
            help="Optional Faker locale (e.g., 'en_US', 'fr_FR').",
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Generate data but do not write to the database.",
        )

    def handle(self, *args, **options):
        count: int = options["count"]
        locale: Optional[str] = options.get("locale")
        dry_run: bool = options.get("dry_run", False)

        fake = Faker(locale) if locale else Faker()

        objects: list[CandidateParty] = []
        for _ in range(count):
            party_name = fake_party_name(fake)
            candidate_name = getattr(fake, "name", lambda: "John Doe")()
            ident = slugify(f"{party_name}-{candidate_name}")

            objects.append(
                CandidateParty(
                    party_name=party_name,
                    candidate_name=candidate_name,
                    identifier=ident,
                )
            )

        if dry_run:
            self.stdout.write(
                self.style.WARNING(
                    f"[dry-run] Prepared {len(objects)} CandidateParty instances (not saved)."
                )
            )
            return

        with transaction.atomic():
            CandidateParty.objects.bulk_create(objects, ignore_conflicts=True)

        self.stdout.write(self.style.SUCCESS(f"Created {len(objects)} CandidateParty records."))

