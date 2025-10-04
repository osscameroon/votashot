from __future__ import annotations

import random
import time
from collections import defaultdict
from random import choice, shuffle
from typing import Dict, List
import os
import csv
from uuid import uuid4
from itertools import cycle

from django.core.management.base import BaseCommand
from django.core.management import call_command
from django.urls import reverse
from rest_framework.test import APIClient

from core.enums import Age, Gender
from core.models import PollOffice, Source, Vote, VoteVerified, Voter, SourceToken


class Command(BaseCommand):
    help = (
        "Continuously simulates voting: ensures enough Sources, "
        "authenticates 5 Sources per PollOffice, then posts votes every 5s."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--count",
            type=int,
            default=100000,
            help="Number of votes to create (default: 100000)",
        )
        parser.add_argument(
            "--sleep",
            type=float,
            default=5.0,
            help="Seconds to sleep between vote rounds (default: 5.0)",
        )

    def handle(self, *args, **options):
        count: int = options["count"]
        sleep_s: float = options["sleep"]
        self.verbosity: int = int(options.get("self.verbosity", 1))

        self.client = APIClient()

        # 1) Ensure there are at least 5x more Sources than PollOffices
        poll_offices = list(PollOffice.objects.all())
        if self.verbosity >= 1:
            self.stdout.write(
                self.style.NOTICE(
                    f"Found {len(poll_offices)} PollOffice(s); targeting {count} votes."
                )
            )
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
        self.auth_url = reverse("authenticate")
        self.vote_url = reverse("vote")

        # Pool of Sources available for registration
        self.set_available_sources()

        shuffle(poll_offices)
        iterator_poll_offices = cycle(poll_offices)

        for i in range(count):
            po: PollOffice = next(iterator_poll_offices)
            source_tokens = self.pick_sources(po)

            self.stdout.write(
                self.style.SUCCESS(
                    f"PollOffice {po.identifier}: registered {len(source_tokens)} sources."
                )
            )

            # 3) Infinite loop: every 5s, each registered source posts a vote
            genders = [Gender.MALE, Gender.FEMALE]
            ages = [Age.LESS_30, Age.LESS_60, Age.MORE_60]

            self.stdout.write(self.style.WARNING("Entering infinite vote loop. Ctrl+C to stop."))
            try:
                last_vote: Vote = Vote.objects.filter(poll_office=po).last()
                if last_vote:
                    index = last_vote.index + 1
                else:
                    index = 1

                sources_to_use_cnt = len(source_tokens)
                sources_to_use_cnt -= choice([0, 1, 0])

                if self.verbosity >= 2:
                    self.stdout.write(
                        self.style.NOTICE(
                            f"PO {po.identifier}: index={index}; posting {sources_to_use_cnt} vote(s)."
                        )
                    )

                for i in range(sources_to_use_cnt):
                    source_token = source_tokens[i]
                    token = source_token.token
                    vote_payload = {
                        # Keep index in a reasonable range to spread votes across multiple ballots
                        "index": index,
                        "gender": random.choice(genders),
                        "age": random.choice(ages),
                        "has_torn": bool(random.getrandbits(1)),
                    }
                    if self.verbosity >= 3:
                        self.stdout.write(
                            self.style.NOTICE(
                                f"PO {po.identifier}: elector={source_token.source.elector_id} -> payload={vote_payload}"
                            )
                        )

                    for _ in range(5):
                        try:
                            resp = self.client.post(
                                self.vote_url,
                                data=vote_payload,
                                format="json",
                                HTTP_AUTHORIZATION=f"Bearer {token}",
                            )
                            if resp.status_code != 200:
                                self.stdout.write(
                                    self.style.WARNING(
                                        f"Vote failed ({po.identifier}): {resp.status_code} {token} {getattr(resp, 'data', None)}"
                                    )
                                )
                            elif self.verbosity >= 3:
                                self.stdout.write(
                                    self.style.SUCCESS(
                                        f"Vote ok ({po.identifier}): index={index}"
                                    )
                                )
                            break
                        except Exception as e:
                            self.stdout.write(self.style.ERROR(str(e)))

                must_verify = choice([True, False, False, False])
                # if must_verify:
                vote = Vote.objects.get(index=index, poll_office=po)
                if VoteVerified.objects.filter(vote=vote).exists():
                    pass
                else:
                    VoteVerified.objects.create(vote=vote,
                                                voter=Voter.objects.create(elector_id=uuid4(), full_name="Random Name"),
                                                # Keep index in a reasonable range to spread votes across multiple ballots
                                                gender=random.choice(genders),
                                                age=random.choice(ages),
                                                has_torn=bool(random.getrandbits(1))
                                                )

                # time.sleep(0.5)
            # Per-vote sleeps already throttle the loop; no extra round sleep here.

            except KeyboardInterrupt:
                self.stdout.write(self.style.WARNING("Stopping vote bot (KeyboardInterrupt)."))
            
    def set_available_sources(self):
        creds_path = os.path.join(os.getcwd(), "sources.csv")
        self.credentials: Dict[str, str] = {}
        if os.path.exists(creds_path):
            try:
                with open(creds_path, newline="", encoding="utf-8") as f:
                    reader = csv.reader(f)
                    header = next(reader, None)
                    for row in reader:
                        if len(row) >= 2:
                            self.credentials[row[0]] = row[1]
                if self.verbosity >= 1:
                    self.stdout.write(
                        self.style.NOTICE(
                            f"Loaded {len(self.credentials)} credential(s) from {creds_path}."
                        )
                    )
            except Exception as e:
                self.stdout.write(self.style.WARNING(f"Could not read sources.csv: {e}"))
        else:
            if self.verbosity >= 1:
                self.stdout.write(
                    self.style.WARNING(
                        f"Credentials file not found at {creds_path}. Newly seeded sources will generate it."
                    )
                )

        self.sources: Dict[str, Source] = {}
        for source in Source.objects.all():
            if not SourceToken.objects.filter(source=source).exists():
                self.sources[source.elector_id] = source
            
    def pick_sources(self, poll_office: PollOffice) -> List[SourceToken]:
        res = SourceToken.objects.filter(poll_office=poll_office)
        if res.exists():
            return list(res)
        
        to_register_nbr = random.randint(2, 5)

        for i in range(to_register_nbr):
            elector_id = list(self.sources.keys())[0]
            source = self.sources.pop(elector_id)
            pwd = self.credentials[elector_id]

            # if not pwd:
            #     if self.verbosity >= 3:
            #         self.stdout.write(
            #             self.style.NOTICE(
            #                 f"PO {po.identifier}: skip {elector_id} (no password in CSV)."
            #             )
            #         )
            #     continue
            payload = {
                "elector_id": elector_id,
                "password": pwd,
                "poll_office_id": poll_office.identifier,
            }
            if self.verbosity >= 3:
                self.stdout.write(
                    self.style.NOTICE(
                        f"PO {poll_office.identifier}: authenticating {elector_id}..."
                    )
                )
            resp = self.client.post(self.auth_url, data=payload, format="json")
            if resp.status_code == 200 and "token" in resp.data:
                if self.verbosity >= 2:
                    self.stdout.write(
                        self.style.SUCCESS(
                            f"PO {poll_office.identifier}: authenticated {elector_id}."
                        )
                    )
            else:
                if self.verbosity >= 3:
                    self.stdout.write(
                        self.style.WARNING(
                            f"PO {poll_office.identifier}: authentication failed for {elector_id} — {resp.status_code} {getattr(resp, 'data', None)}"
                        )
                    )

        return list(SourceToken.objects.filter(poll_office=poll_office))
        
