from __future__ import annotations

import asyncio
import aiohttp
import json
import os
import random
import time
from collections import defaultdict
from typing import Dict, List, Optional

from django.conf import settings
from django.core.management.base import BaseCommand

from core.models import PollOffice, VotingPaperResult


class Command(BaseCommand):
    help = (
        "High-performance asyncio VPR simulation: loads source tokens and posts "
        "real HTTP requests to /api/votingpaperresult/."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--count",
            type=int,
            default=10000,
            help="Number of VPR proposals to submit (default: 10000)",
        )
        parser.add_argument(
            "--concurrent",
            type=int,
            default=100,
            help="Number of concurrent requests (default: 100)",
        )
        parser.add_argument(
            "--server-url",
            type=str,
            default="http://localhost:8000",
            help="Server base URL (default: http://localhost:8000)",
        )
        parser.add_argument(
            "--batch-size",
            type=int,
            default=50,
            help="Proposals per batch for a single office/index (default: 50)",
        )
        parser.add_argument(
            "--tokens-file",
            type=str,
            default="source_tokens.json",
            help="Path to JSON with pre-authenticated source tokens (default: source_tokens.json)",
        )

    def handle(self, *args, **options):
        self.total_count = int(options["count"]) or 0
        self.concurrent = int(options["concurrent"]) or 1
        self.server_url = options["server_url"].rstrip("/")
        self.batch_size = int(options["batch_size"]) or 1
        self.tokens_file = options["tokens_file"]
        self.verbosity = int(options.get("verbosity", 1))

        self.vpr_url = f"{self.server_url}/api/votingpaperresult/"

        self.stdout.write(
            self.style.NOTICE(
                f"Starting asyncio VPR simulation:\n"
                f"  Proposals: {self.total_count}\n"
                f"  Concurrency: {self.concurrent}\n"
                f"  Batch size: {self.batch_size}\n"
                f"  Server: {self.server_url}"
            )
        )

        try:
            asyncio.run(self.async_main())
        except KeyboardInterrupt:
            self.stdout.write(self.style.WARNING("Interrupted by user"))

    async def async_main(self):
        start_time = time.time()

        # 1) Load poll offices and candidate parties (from files under BASE_DIR)
        poll_offices = await self.load_poll_offices()
        if not poll_offices:
            return

        party_identifiers = self.load_candidate_party_identifiers()
        if not party_identifiers:
            self.stdout.write(self.style.ERROR("No CandidateParty found; aborting."))
            return

        # 2) Load pre-authenticated tokens
        tokens_by_office = self.load_tokens_from_file(poll_offices)
        if not any(tokens_by_office.values()):
            self.stdout.write(
                self.style.ERROR(
                    f"No tokens loaded from {self.tokens_file}. Aborting."
                )
            )
            return

        # 3) Determine starting index per poll office based on DB state
        next_index_by_office = self.compute_next_indices(tokens_by_office)
        if not next_index_by_office:
            self.stdout.write(self.style.ERROR("Failed to compute starting indices."))
            return

        # 4) Run submission
        await self.run_vpr_submission(
            poll_offices,
            tokens_by_office,
            party_identifiers,
            next_index_by_office,
        )

        elapsed = time.time() - start_time
        rate = (self.total_count / elapsed) if elapsed > 0 else 0
        self.stdout.write(
            self.style.SUCCESS(
                f"Completed {self.total_count} proposals in {elapsed:.2f}s ({rate:.0f}/s)"
            )
        )

    async def load_poll_offices(self) -> List[PollOffice]:
        """Load poll offices from poll_offices.json for quick access."""
        try:
            with (settings.BASE_DIR / "poll_offices.json").open() as fp:
                data = json.load(fp)
            offices = [PollOffice(**row) for row in data]
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Failed loading poll_offices.json: {e}"))
            return []

        if self.verbosity >= 1:
            self.stdout.write(self.style.SUCCESS(f"Found {len(offices)} poll offices"))
        return offices

    def load_candidate_party_identifiers(self) -> List[str]:
        """Load party identifiers from candidate_parties.json in BASE_DIR."""
        try:
            with (settings.BASE_DIR / "candidate_parties.json").open() as fp:
                data = json.load(fp)
            ids = [row.get("identifier") for row in data if isinstance(row, dict) and row.get("identifier")]
            if self.verbosity >= 1:
                self.stdout.write(self.style.SUCCESS(f"Loaded {len(ids)} candidate parties"))
            return ids
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Failed loading candidate_parties.json: {e}"))
            return []

    def load_tokens_from_file(self, poll_offices: List[PollOffice]) -> Dict[str, List[Dict]]:
        """Load pre-authenticated tokens per poll office from JSON file.

        Expected format: {"<poll_office_identifier>": [ {"token": "...", ...}, ... ]}
        Returns mapping: office.identifier -> list of {'token': str}
        """
        path = os.path.join(os.getcwd(), self.tokens_file)
        tokens_by_office: Dict[str, List[Dict]] = defaultdict(list)

        if not os.path.exists(path):
            if self.verbosity >= 2:
                self.stdout.write(self.style.WARNING(f"Tokens file not found: {path}"))
            return tokens_by_office

        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)

            valid_office_ids = {po.identifier for po in poll_offices}

            loaded_offices = 0
            loaded_tokens = 0
            for office_id, responses in data.items():
                if office_id not in valid_office_ids:
                    continue
                if not isinstance(responses, list):
                    continue
                for item in responses:
                    if isinstance(item, dict) and "token" in item:
                        tokens_by_office[office_id].append({"token": item["token"]})
                        loaded_tokens += 1
                if tokens_by_office[office_id]:
                    loaded_offices += 1

            if self.verbosity >= 1:
                self.stdout.write(
                    self.style.SUCCESS(
                        f"Loaded {loaded_tokens} tokens for {loaded_offices} poll offices"
                    )
                )
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Failed to read tokens from {path}: {e}"))

        return tokens_by_office

    def compute_next_indices(self, tokens_by_office: Dict[str, List[Dict]]) -> Dict[str, int]:
        """Compute starting next index per office, based on DB's last VotingPaperResult index.

        Offices without any prior results start at 0 (so next is 1).
        """
        next_map: Dict[str, int] = {}
        for office_id, token_list in tokens_by_office.items():
            if not token_list:
                continue
            try:
                office = PollOffice.objects.get(identifier=office_id)
                last = (
                    VotingPaperResult.objects.filter(poll_office=office)
                    .order_by("index")
                    .last()
                )
                next_map[office_id] = (last.index if last else 0)
            except PollOffice.DoesNotExist:
                # Skip unknown office ids
                continue
        if self.verbosity >= 2:
            self.stdout.write(self.style.NOTICE(f"Computed next indices for {len(next_map)} offices"))
        return next_map

    async def run_vpr_submission(
        self,
        poll_offices: List[PollOffice],
        tokens_by_office: Dict[str, List[Dict]],
        party_ids: List[str],
        next_index_by_office: Dict[str, int],
    ) -> None:
        self.proposals_completed = 0
        self.proposals_failed = 0

        semaphore = asyncio.Semaphore(self.concurrent)

        async with aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=30),
            connector=aiohttp.TCPConnector(limit=self.concurrent * 2),
        ) as session:
            tasks: List[asyncio.Task] = []

            remaining = self.total_count
            batch_id = 0

            # Pre-build a list of offices that have tokens
            offices_with_tokens = [
                po for po in poll_offices if tokens_by_office.get(po.identifier)
            ]
            if not offices_with_tokens:
                self.stdout.write(self.style.ERROR("No poll offices have authenticated tokens"))
                return

            while remaining > 0:
                # Pick an office that has tokens
                po = random.choice(offices_with_tokens)
                office_id = po.identifier

                # Determine next index for this office (one index per batch)
                current_index = next_index_by_office.get(office_id, 0) + 1
                next_index_by_office[office_id] = current_index

                proposals_in_batch = min(self.batch_size, remaining, len(tokens_by_office[office_id]))
                task = self.process_vpr_batch(
                    session,
                    semaphore,
                    batch_id,
                    office_id,
                    current_index,
                    tokens_by_office[office_id],
                    party_ids,
                    proposals_in_batch,
                )
                tasks.append(task)

                remaining -= proposals_in_batch
                batch_id += 1

            # Progress monitor
            progress_task = asyncio.create_task(self.monitor_progress())

            await asyncio.gather(*tasks, return_exceptions=True)

            progress_task.cancel()
            try:
                await progress_task
            except asyncio.CancelledError:
                pass

        self.stdout.write(
            self.style.SUCCESS(
                f"Proposals completed: {self.proposals_completed} ok, {self.proposals_failed} failed"
            )
        )

    async def process_vpr_batch(
        self,
        session: aiohttp.ClientSession,
        semaphore: asyncio.Semaphore,
        batch_id: int,
        office_id: str,
        index_value: int,
        office_tokens: List[Dict],
        party_ids: List[str],
        proposals_count: int,
    ) -> None:
        # Build tasks for this batch: same index across multiple sources
        tasks: List[asyncio.Task] = []
        for i in range(proposals_count):
            token_info = office_tokens[i % len(office_tokens)]
            payload = {
                "index": index_value,
                "party_id": random.choice(party_ids),
            }
            tasks.append(
                self.submit_single_vpr(session, semaphore, token_info["token"], payload)
            )

        results = await asyncio.gather(*tasks, return_exceptions=True)
        ok = sum(1 for r in results if r is True)
        ko = len(results) - ok
        self.proposals_completed += ok
        self.proposals_failed += ko

    async def submit_single_vpr(
        self,
        session: aiohttp.ClientSession,
        semaphore: asyncio.Semaphore,
        token: str,
        payload: Dict,
    ) -> bool:
        async with semaphore:
            headers = {"Authorization": f"Bearer {token}"}
            try:
                async with session.post(self.vpr_url, json=payload, headers=headers) as resp:
                    success = resp.status == 200
                    if not success and self.verbosity >= 3:
                        text = await resp.text()
                        self.stdout.write(
                            f"VPR failed: {resp.status} {text} payload={payload}"
                        )
                    return success
            except Exception as e:
                if self.verbosity >= 2:
                    self.stdout.write(f"VPR exception: {e}")
                return False

    async def monitor_progress(self):
        last_completed = 0
        while True:
            await asyncio.sleep(2)
            current = self.proposals_completed
            rate = (current - last_completed) / 2
            if self.verbosity >= 1 and self.total_count:
                pct = (current / self.total_count) * 100
                self.stdout.write(
                    f"Progress: {current}/{self.total_count} ({pct:.1f}%) - {rate:.0f} req/s"
                )
            last_completed = current
            if current >= self.total_count:
                break
