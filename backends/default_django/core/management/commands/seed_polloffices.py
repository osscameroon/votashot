from __future__ import annotations

import random
import string
from typing import Optional

from django.core.management.base import BaseCommand
from django.db import transaction
from faker import Faker

from core.models import PollOffice


def safe_fake_attr(fake: Faker, attr: str) -> Optional[str]:
    """Return a faker attribute if present, else None."""
    fn = getattr(fake, attr, None)
    if callable(fn):
        try:
            return fn()
        except Exception:
            return None
    return None


def random_identifier(fake: Faker) -> str:
    base = fake.unique.bothify(text="????-#####").upper()
    cc = safe_fake_attr(fake, "country_code") or "XX"
    return f"{cc}-{base}"


class Command(BaseCommand):
    help = "Create fake PollOffice entries using Faker."

    def add_arguments(self, parser):
        parser.add_argument(
            "--count",
            type=int,
            default=10,
            help="Number of PollOffice records to create (default: 10)",
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

        objects: list[PollOffice] = []

        for _ in range(count):
            name = f"Poll Office {fake.city()} #{random.randint(1, 9999)}"
            identifier = random_identifier(fake)
            country = safe_fake_attr(fake, "country") or "Unknown"
            state = safe_fake_attr(fake, "state")
            region = safe_fake_attr(fake, "region") or safe_fake_attr(fake, "state_abbr")
            city = safe_fake_attr(fake, "city")
            county = safe_fake_attr(fake, "county") or safe_fake_attr(fake, "province")
            district = safe_fake_attr(fake, "district") or safe_fake_attr(fake, "borough")

            objects.append(
                PollOffice(
                    name=name,
                    identifier=identifier,
                    country=country,
                    state=state,
                    region=region,
                    city=city,
                    county=county,
                    district=district,
                )
            )

        if dry_run:
            self.stdout.write(self.style.WARNING(f"[dry-run] Prepared {len(objects)} PollOffice instances (not saved)."))
            return

        with transaction.atomic():
            PollOffice.objects.bulk_create(objects, ignore_conflicts=True)

        self.stdout.write(self.style.SUCCESS(f"Created {len(objects)} PollOffice records."))

