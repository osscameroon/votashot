from __future__ import annotations

import random
from typing import Optional
import csv
import os

from django.core.management.base import BaseCommand
from django.db import transaction
from faker import Faker

from core.enums import SourceType
from core.models import Source


def generate_elector_id() -> str:
    """Generate an elector_id like 02-12-069-0080-16-000550.

    Pattern: 2-2-3-4-2-6 digits (zero-padded), joined by dashes.
    """
    parts = [
        f"{random.randint(0, 99):02d}",
        f"{random.randint(0, 99):02d}",
        f"{random.randint(0, 999):03d}",
        f"{random.randint(0, 9999):04d}",
        f"{random.randint(0, 99):02d}",
        f"{random.randint(0, 999999):06d}",
    ]
    return "-".join(parts)


class Command(BaseCommand):
    help = "Create fake Source entries using Faker with proper password hashing."

    def add_arguments(self, parser):
        parser.add_argument(
            "--count",
            type=int,
            default=10,
            help="Number of Source records to create (default: 10)",
        )
        parser.add_argument(
            "--locale",
            type=str,
            default=None,
            help="Optional Faker locale (e.g., 'en_US', 'fr_FR').",
        )
        choices = [c[0] for c in SourceType.choices()]
        parser.add_argument(
            "--password",
            type=str,
            default=None,
            help="Raw password to set on all created Sources (defaults to Faker password).",
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Generate data but do not write to the database.",
        )

    def handle(self, *args, **options):
        count: int = options["count"]
        locale: Optional[str] = options.get("locale")
        raw_password: Optional[str] = options.get("password")
        dry_run: bool = options.get("dry_run", False)

        fake = Faker(locale) if locale else Faker()

        created = 0
        prepared: list[tuple[Source, str]] = []  # (instance, raw_password)

        for _ in range(count):
            # Ensure unique elector_id within this run and DB
            for _attempt in range(20):
                elector_id = generate_elector_id()
                if not Source.objects.filter(elector_id=elector_id).exists() and all(
                    s[0].elector_id != elector_id for s in prepared
                ):
                    break
            else:
                # Fallback: extremely unlikely; still proceed with possibly duplicate id
                elector_id = generate_elector_id()

            full_name = getattr(fake, "name", lambda: None)()
            email = getattr(fake, "email", lambda: None)()
            phone = getattr(fake, "phone_number", lambda: None)()
            password_to_use = raw_password or fake.password(length=12)

            stype = random.choice([SourceType.OFFICIAL, SourceType.INDEPENDANT,
                                   SourceType.POLITICAL_PARTY, SourceType.INDEPENDANT])

            if stype == SourceType.OFFICIAL:
                official_org = getattr(fake, "company", lambda: None)()
            else:
                official_org = None

            source = Source(
                elector_id=elector_id,
                type=stype,
                official_org=official_org,
                full_name=full_name,
                email=email,
                phone_number=phone,
            )
            # Ensure password is properly hashed and user is synced
            source.set_password(password_to_use)
            prepared.append((source, password_to_use))

        # Write generated credentials to CSV (append mode, add header if new file)
        csv_path = os.path.join(os.getcwd(), "sources.csv")
        file_exists = os.path.exists(csv_path)
        with open(csv_path, "a", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            if not file_exists or os.stat(csv_path).st_size == 0:
                writer.writerow(["elector_id", "password"])  # header
            for s, pwd in prepared:
                writer.writerow([s.elector_id, pwd])

        if dry_run:
            self.stdout.write(
                self.style.WARNING(
                    f"[dry-run] Prepared {len(prepared)} Source instances (not saved)."
                )
            )
            return

        with transaction.atomic():
            for s, _ in prepared:
                s.save()
                created += 1

        self.stdout.write(self.style.SUCCESS(f"Created {created} Source records."))
