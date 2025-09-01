from __future__ import annotations

import random
import time
from collections import defaultdict
from typing import Dict, List
import os
import csv

from django.core.management.base import BaseCommand
from django.core.management import call_command
from django.urls import reverse
from rest_framework.test import APIClient

from core.enums import Age, Gender
from core.models import PollOffice, Source


class Command(BaseCommand):
    help = (
        "Continuously simulates voting: ensures enough Sources, "
        "authenticates 5 Sources per PollOffice, then posts votes every 5s."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--per-office",
            type=int,
            default=5,
            help="Number of sources to authenticate per poll office (default: 5)",
        )
        parser.add_argument(
            "--sleep",
            type=float,
            default=5.0,
            help="Seconds to sleep between vote rounds (default: 5.0)",
        )

    def handle(self, *args, **options):
        per_office: int = options["per_office"]
        sleep_s: float = options["sleep"]

        client = APIClient()

        # 1) Ensure there are at least 5x more Sources than PollOffices
        poll_offices = list(PollOffice.objects.all())
        if not poll_offices:
            self.stdout.write(
                self.style.WARNING(
                    "No PollOffice found. Seed poll offices first (seed_polloffices)."
                )
            )
            return

        need_total = 5 * len(poll_offices)
        current_sources = Source.objects.count()
        if current_sources < need_total:
            to_create = need_total - current_sources
            self.stdout.write(
                self.style.WARNING(
                    f"Seeding {to_create} Sources to reach {need_total} minimum (5x offices)."
                )
            )
            # Use the existing seed_sources command
            # Seed with random passwords; they will be stored in sources.csv
            call_command("seed_sources", count=to_create)
        else:
            self.stdout.write(
                self.style.SUCCESS(
                    f"Sources already sufficient: {current_sources} >= {need_total}."
                )
            )

        # 2) For each PollOffice, authenticate at least `per_office` existing sources.
        #    Use authenticate endpoint with passwords loaded strictly from sources.csv.
        auth_url = reverse("authenticate")
        vote_url = reverse("vote")

        # registered_sources keeps authentication result per poll office
        # Structure: { poll_office_id (int): [ {"elector_id": str, "token": str}, ... ] }
        registered_sources: Dict[int, List[dict]] = defaultdict(list)

        # Load credentials from sources.csv if present
        creds_path = os.path.join(os.getcwd(), "sources.csv")
        credentials: Dict[str, str] = {}
        if os.path.exists(creds_path):
            try:
                with open(creds_path, newline="", encoding="utf-8") as f:
                    reader = csv.reader(f)
                    header = next(reader, None)
                    for row in reader:
                        if len(row) >= 2:
                            credentials[row[0]] = row[1]
            except Exception as e:
                self.stdout.write(self.style.WARNING(f"Could not read sources.csv: {e}"))

        # Pool of Sources available for registration
        all_sources: List[Source] = list(Source.objects.all().order_by("id"))
        random.shuffle(all_sources)
        eligible_sources = [s for s in all_sources if s.elector_id in credentials]

        for po in poll_offices:
            attempts = 0
            while len(registered_sources[po.id]) < per_office and attempts < 10:
                attempts += 1
                needed = per_office - len(registered_sources[po.id])
                used = 0
                for s in eligible_sources:
                    if used >= needed:
                        break
                    elector_id = s.elector_id
                    if any(r["elector_id"] == elector_id for r in registered_sources[po.id]):
                        continue
                    pwd = credentials.get(elector_id)
                    if not pwd:
                        continue
                    payload = {
                        "elector_id": elector_id,
                        "password": pwd,
                        "poll_office_id": po.identifier,
                    }
                    resp = client.post(auth_url, data=payload, format="json")
                    if resp.status_code == 200 and "token" in resp.data:
                        registered_sources[po.id].append(
                            {"elector_id": elector_id, "token": resp.data["token"]}
                        )
                        used += 1
                # If still short, seed a few more new Sources (random passwords) and refresh pools
                if len(registered_sources[po.id]) < per_office:
                    missing = per_office - len(registered_sources[po.id])
                    call_command("seed_sources", count=missing)
                    # reload pools and creds
                    try:
                        with open(creds_path, newline="", encoding="utf-8") as f:
                            reader = csv.reader(f)
                            header = next(reader, None)
                            for row in reader:
                                if len(row) >= 2:
                                    credentials[row[0]] = row[1]
                    except Exception:
                        pass
                    all_sources = list(Source.objects.all().order_by("id"))
                    random.shuffle(all_sources)
                    eligible_sources = [s for s in all_sources if s.elector_id in credentials]

            self.stdout.write(
                self.style.SUCCESS(
                    f"PollOffice {po.identifier}: registered {len(registered_sources[po.id])} sources."
                )
            )

        # 3) Infinite loop: every 5s, each registered source posts a vote
        genders = [Gender.MALE, Gender.FEMALE]
        ages = [Age.LESS_30, Age.LESS_60, Age.MORE_60]

        poll_offices_indexes: Dict[int, int] = {}

        self.stdout.write(self.style.WARNING("Entering infinite vote loop. Ctrl+C to stop."))
        try:
            while True:
                for po in poll_offices:
                    index = poll_offices_indexes.get(po.id, 0)
                    index += 1
                    poll_offices_indexes[po.id] = index

                    for reg in registered_sources.get(po.id, []):
                        token = reg["token"]
                        vote_payload = {
                            # Keep index in a reasonable range to spread votes across multiple ballots
                            "index": index,
                            "gender": random.choice(genders),
                            "age": random.choice(ages),
                            "has_torn": bool(random.getrandbits(1)),
                        }
                        resp = client.post(
                            vote_url,
                            data=vote_payload,
                            format="json",
                            HTTP_AUTHORIZATION=f"Bearer {token}",
                        )
                        if resp.status_code != 200:
                            self.stdout.write(
                                self.style.WARNING(
                                    f"Vote failed ({po.identifier}): {resp.status_code} {getattr(resp, 'data', None)}"
                                )
                            )
                        time.sleep(0.5)
        except KeyboardInterrupt:
            self.stdout.write(self.style.WARNING("Stopping vote bot (KeyboardInterrupt)."))
