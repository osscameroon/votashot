from __future__ import annotations

import asyncio
import aiohttp
import random
import time
import csv
import os
import json
from collections import defaultdict
from random import choice
from typing import Dict, List, Optional
from uuid import uuid4

from django.conf import settings
from django.core.management.base import BaseCommand
from django.core.management import call_command

from core.enums import Age, Gender
from core.models import PollOffice, Source


class Command(BaseCommand):
    help = "High-performance asyncio voting simulation with real HTTP requests to localhost:8000"

    def add_arguments(self, parser):
        parser.add_argument(
            "--count", type=int, default=100000,
            help="Number of votes to create (default: 100000)"
        )
        parser.add_argument(
            "--concurrent", type=int, default=100,
            help="Number of concurrent requests (default: 100)"
        )
        parser.add_argument(
            "--server-url", type=str, default="http://localhost:8000",
            help="Server URL (default: http://localhost:8000)"
        )
        parser.add_argument(
            "--pre-auth", type=int, default=500,
            help="Number of sources to pre-authenticate (default: 500)"
        )
        parser.add_argument(
            "--batch-size", type=int, default=50,
            help="Votes per batch (default: 50)"
        )
        parser.add_argument(
            "--tokens-file", type=str, default="source_tokens.json",
            help="Path to JSON file containing pre-authenticated source tokens by poll office"
        )

    def handle(self, *args, **options):
        self.count = options["count"]
        self.concurrent = options["concurrent"]
        self.server_url = options["server_url"].rstrip('/')
        self.pre_auth_count = options["pre_auth"]
        self.batch_size = options["batch_size"]
        self.verbosity = int(options.get("verbosity", 1))
        self.tokens_file = options["tokens_file"]

        # Setup URLs
        self.auth_url = f"{self.server_url}/api/authenticate/"  # Adjust path as needed
        self.vote_url = f"{self.server_url}/api/vote/"  # Adjust path as needed

        self.stdout.write(
            self.style.NOTICE(
                f"Starting asyncio voting simulation:\n"
                f"  Target: {self.count} votes\n"
                f"  Concurrency: {self.concurrent}\n"
                f"  Server: {self.server_url}\n"
                f"  Pre-auth: {self.pre_auth_count} sources"
            )
        )

        # Run the async main function
        try:
            asyncio.run(self.async_main())
        except KeyboardInterrupt:
            self.stdout.write(self.style.WARNING("Interrupted by user"))

    async def async_main(self):
        """Main async function"""
        start_time = time.time()

        # 1. Setup and validation
        poll_offices = await self.setup_poll_offices()
        if not poll_offices:
            return

        # 2. Load pre-authenticated tokens from file ONLY
        authenticated_tokens = self.load_tokens_from_file(poll_offices)

        # Abort if no tokens are available
        if not any(authenticated_tokens.values()):
            self.stdout.write(self.style.ERROR(
                f"No tokens loaded from {self.tokens_file}. Aborting."
            ))
            return

        if not any(authenticated_tokens.values()):
            self.stdout.write(self.style.ERROR("No sources were authenticated. Cannot proceed."))
            return

        # 5. Run voting simulation
        await self.run_voting_simulation(poll_offices, authenticated_tokens)

        elapsed = time.time() - start_time
        rate = self.count / elapsed if elapsed > 0 else 0
        self.stdout.write(
            self.style.SUCCESS(
                f"✅ Completed {self.count} votes in {elapsed:.2f}s ({rate:.0f} votes/sec)"
            )
        )

    async def setup_poll_offices(self) -> List[PollOffice]:
        """Setup poll offices"""
        with (settings.BASE_DIR / "poll_offices.json").open() as fp:
            poll_offices = [PollOffice(**row) for row in json.load(fp)]

        if not poll_offices:
            self.stdout.write(self.style.WARNING("No PollOffices found. Please create some first."))
            return []

        self.stdout.write(
            self.style.SUCCESS(f"Found {len(poll_offices)} poll offices")
        )
        return poll_offices

    def load_tokens_from_file(self, poll_offices) -> Dict[str, List[Dict]]:
        """Load pre-authenticated tokens per poll office from JSON file.

        Expected format: {"<poll_office_identifier>": [ {"token": "...", ...}, ... ]}

        Returns a dict mapping poll_office.identifier -> list of dicts with 'token' key.
        Unknown or malformed entries are ignored.
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

            # Build a quick set of valid poll office identifiers
            valid_office_ids = {po.identifier for po in poll_offices}

            loaded_offices = 0
            loaded_tokens = 0
            for office_id, responses in data.items():
                if office_id not in valid_office_ids:
                    continue
                if not isinstance(responses, list):
                    continue
                for item in responses:
                    if isinstance(item, dict) and 'token' in item:
                        tokens_by_office[office_id].append({'token': item['token']})
                        loaded_tokens += 1
                if tokens_by_office[office_id]:
                    loaded_offices += 1

            if self.verbosity >= 1:
                self.stdout.write(self.style.SUCCESS(
                    f"Loaded {loaded_tokens} tokens for {loaded_offices} poll offices from {self.tokens_file}"
                ))

        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Failed to read tokens from {path}: {e}"))

        return tokens_by_office

    async def run_voting_simulation(self, poll_offices, authenticated_tokens):
        """Run the main voting simulation"""
        self.stdout.write(self.style.NOTICE("Starting voting simulation..."))

        # Create voting tasks
        vote_tasks = []
        semaphore = asyncio.Semaphore(self.concurrent)

        # Progress tracking
        self.votes_completed = 0
        self.votes_failed = 0

        async with aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=30),
                connector=aiohttp.TCPConnector(limit=self.concurrent * 2)
        ) as session:

            # Generate batches of votes
            remaining_votes = self.count
            batch_id = 0

            while remaining_votes > 0:
                batch_votes = min(self.batch_size, remaining_votes)

                # Select poll office with authenticated tokens
                poll_office = self.select_poll_office_with_tokens(poll_offices, authenticated_tokens)
                if not poll_office:
                    self.stdout.write(self.style.ERROR("No poll offices have authenticated tokens"))
                    break

                # Create voting task
                task = self.process_vote_batch(
                    session, semaphore, batch_id, poll_office,
                    authenticated_tokens[poll_office.identifier], batch_votes
                )
                vote_tasks.append(task)

                remaining_votes -= batch_votes
                batch_id += 1

            # Start progress monitoring
            progress_task = asyncio.create_task(self.monitor_progress())

            # Execute all voting tasks
            await asyncio.gather(*vote_tasks, return_exceptions=True)

            # Stop progress monitoring
            progress_task.cancel()
            try:
                await progress_task
            except asyncio.CancelledError:
                pass

        self.stdout.write(
            self.style.SUCCESS(
                f"Voting completed: {self.votes_completed} successful, {self.votes_failed} failed"
            )
        )

    def select_poll_office_with_tokens(self, poll_offices, authenticated_tokens):
        """Select a poll office that has authenticated tokens"""
        offices_with_tokens = [
            office for office in poll_offices
            if authenticated_tokens[office.identifier]
        ]
        return choice(offices_with_tokens) if offices_with_tokens else None

    async def process_vote_batch(
            self,
            session: aiohttp.ClientSession,
            semaphore: asyncio.Semaphore,
            batch_id: int,
            poll_office: PollOffice,
            office_tokens: List[Dict],
            vote_count: int
    ):
        """Process a batch of votes for a specific poll office"""
        genders = [Gender.MALE, Gender.FEMALE]
        ages = [Age.LESS_30, Age.LESS_60, Age.MORE_60]

        # Create individual vote tasks for this batch
        vote_tasks = []

        for i in range(vote_count):
            # Select token (round-robin through available tokens)
            token_info = office_tokens[i % len(office_tokens)]

            # Generate vote payload
            vote_payload = {
                "index": batch_id * self.batch_size + i + 1,  # Simple index generation
                "gender": random.choice(genders),
                "age": random.choice(ages),
                "has_torn": bool(random.getrandbits(1)),
            }

            # Create vote task
            task = self.submit_single_vote(
                session, semaphore, token_info['token'], vote_payload
            )
            vote_tasks.append(task)

        # Execute all votes in this batch
        results = await asyncio.gather(*vote_tasks, return_exceptions=True)

        # Count results
        batch_successful = sum(1 for r in results if r is True)
        batch_failed = len(results) - batch_successful

        self.votes_completed += batch_successful
        self.votes_failed += batch_failed

    async def submit_single_vote(
            self,
            session: aiohttp.ClientSession,
            semaphore: asyncio.Semaphore,
            token: str,
            vote_payload: Dict
    ) -> bool:
        """Submit a single vote"""
        async with semaphore:
            headers = {"Authorization": f"Bearer {token}"}

            try:
                async with session.post(
                        self.vote_url,
                        json=vote_payload,
                        headers=headers
                ) as response:
                    success = response.status == 200

                    if not success and self.verbosity >= 3:
                        error_text = await response.text()
                        self.stdout.write(f"Vote failed: {response.status} {error_text}")

                    return success

            except Exception as e:
                if self.verbosity >= 2:
                    self.stdout.write(f"Vote exception: {e}")
                return False

    async def monitor_progress(self):
        """Monitor and display progress"""
        last_completed = 0

        while True:
            await asyncio.sleep(2)  # Update every 2 seconds

            current_completed = self.votes_completed
            rate = (current_completed - last_completed) / 2  # votes per second

            if self.verbosity >= 1:
                progress = (current_completed / self.count) * 100
                self.stdout.write(
                    f"Progress: {current_completed}/{self.count} ({progress:.1f}%) "
                    f"- {rate:.0f} votes/sec"
                )

            last_completed = current_completed

            if current_completed >= self.count:
                break
