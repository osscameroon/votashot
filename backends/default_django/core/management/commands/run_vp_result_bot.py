from __future__ import annotations

import csv
import os
import random
import time
from collections import defaultdict
from typing import Dict, List

from django.core.management import call_command
from django.core.management.base import BaseCommand
from django.urls import reverse
from rest_framework.test import APIClient

from core.models import CandidateParty, PollOffice, Source


class Command(BaseCommand):
    help = (
        "Continuously simulates voting paper results: ensures enough Sources and CandidateParties, "
        "authenticates N Sources per PollOffice, then posts results every few seconds."
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
            help="Seconds to sleep between rounds (default: 5.0)",
        )
        parser.add_argument(
            "--min-parties",
            type=int,
            default=5,
            help="Ensure at least this many CandidateParty records (default: 5)",
        )

    def handle(self, *args, **options):
        per_office: int = options["per_office"]
        sleep_s: float = options["sleep"]
        min_parties: int = options["min_parties"]

        client = APIClient()

        # 1) Ensure PollOffices exist
        poll_offices = list(PollOffice.objects.all())
        if not poll_offices:
            self.stdout.write(
                self.style.WARNING(
                    "No PollOffice found. Seed poll offices first (seed_polloffices)."
                )
            )
            return

        # 2) Ensure there are enough Sources (same heuristic as run_vote_bot: 5x offices)
        need_total_sources = 5 * len(poll_offices)
        current_sources = Source.objects.count()
        if current_sources < need_total_sources:
            to_create = need_total_sources - current_sources
            self.stdout.write(
                self.style.WARNING(
                    f"Seeding {to_create} Sources to reach {need_total_sources} minimum (5x offices)."
                )
            )
            call_command("seed_sources", count=to_create)
        else:
            self.stdout.write(
                self.style.SUCCESS(
                    f"Sources already sufficient: {current_sources} >= {need_total_sources}."
                )
            )

        # 3) Ensure there are some CandidateParties to choose from
        current_parties = CandidateParty.objects.count()
        if current_parties < min_parties:
            to_create = max(0, min_parties - current_parties)
            if to_create > 0:
                self.stdout.write(
                    self.style.WARNING(
                        f"Seeding {to_create} CandidateParty records to reach {min_parties}."
                    )
                )
                call_command("seed_candidateparties", count=to_create)
        party_identifiers: List[str] = list(
            CandidateParty.objects.values_list("identifier", flat=True)
        )
        if not party_identifiers:
            self.stdout.write(
                self.style.ERROR("No CandidateParty available; cannot proceed.")
            )
            return

        # 4) Authenticate per PollOffice using credentials from sources.csv
        auth_url = reverse("authenticate")
        vpr_url = reverse("voting-paper-result")

        registered_sources: Dict[int, List[dict]] = defaultdict(list)

        creds_path = os.path.join(os.getcwd(), "sources.csv")
        credentials: Dict[str, str] = {}
        if os.path.exists(creds_path):
            try:
                with open(creds_path, newline="", encoding="utf-8") as f:
                    reader = csv.reader(f)
                    _ = next(reader, None)  # header
                    for row in reader:
                        if len(row) >= 2:
                            credentials[row[0]] = row[1]
            except Exception as e:
                self.stdout.write(self.style.WARNING(f"Could not read sources.csv: {e}"))

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
                if len(registered_sources[po.id]) < per_office:
                    missing = per_office - len(registered_sources[po.id])
                    call_command("seed_sources", count=missing)
                    # refresh credentials and source pools
                    try:
                        with open(creds_path, newline="", encoding="utf-8") as f:
                            reader = csv.reader(f)
                            _ = next(reader, None)
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

        # 5) Infinite loop: each registered source posts a voting paper result
        poll_offices_indexes: Dict[int, int] = {}
        self.stdout.write(
            self.style.WARNING("Entering infinite voting paper result loop. Ctrl+C to stop.")
        )
        try:
            while True:
                for po in poll_offices:
                    index = poll_offices_indexes.get(po.id, 0) + 1
                    poll_offices_indexes[po.id] = index

                    for reg in registered_sources.get(po.id, []):
                        token = reg["token"]
                        payload = {
                            "index": index,
                            "party_id": random.choice(party_identifiers),
                        }
                        resp = client.post(
                            vpr_url,
                            data=payload,
                            format="json",
                            HTTP_AUTHORIZATION=f"Bearer {token}",
                        )
                        if resp.status_code != 200:
                            self.stdout.write(
                                self.style.WARNING(
                                    f"VPR failed ({po.identifier}): {resp.status_code} {getattr(resp, 'data', None)}"
                                )
                            )
                        time.sleep(0.5)

        except KeyboardInterrupt:
            self.stdout.write(self.style.WARNING("Stopping VPR bot (KeyboardInterrupt)."))

