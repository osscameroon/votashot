from __future__ import annotations

import asyncio
import aiohttp
import random
import time
import csv
import os
from collections import defaultdict
from random import choice
from typing import Dict, List, Optional
from uuid import uuid4

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

    def handle(self, *args, **options):
        self.count = options["count"]
        self.concurrent = options["concurrent"]
        self.server_url = options["server_url"].rstrip('/')
        self.pre_auth_count = options["pre_auth"]
        self.batch_size = options["batch_size"]
        self.verbosity = int(options.get("verbosity", 1))

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

        # 2. Ensure sufficient sources
        await self.ensure_sources(poll_offices)

        # 3. Load credentials
        await self.load_credentials()

        # 4. Pre-authenticate sources
        authenticated_tokens = await self.pre_authenticate_sources(poll_offices)

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
        poll_offices = []
        async for tmp in PollOffice.objects.all():
            poll_offices.append(tmp)

        if not poll_offices:
            self.stdout.write(self.style.WARNING("No PollOffices found. Please create some first."))
            return []

        self.stdout.write(
            self.style.SUCCESS(f"Found {len(poll_offices)} poll offices")
        )
        return poll_offices

    async def ensure_sources(self, poll_offices):
        """Ensure we have enough sources"""
        need_total = max(self.pre_auth_count, 5 * len(poll_offices))
        current_sources = await Source.objects.acount()

        if current_sources < need_total:
            to_create = need_total - current_sources
            self.stdout.write(self.style.WARNING(f"No sufficient sources found. Please create {to_create} first."))
            return []

    async def load_credentials(self):
        """Load source credentials from CSV"""
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

                self.stdout.write(
                    self.style.SUCCESS(f"Loaded {len(self.credentials)} credentials")
                )
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"Could not read sources.csv: {e}"))
        else:
            self.stdout.write(self.style.WARNING("sources.csv not found"))

    async def pre_authenticate_sources(self, poll_offices) -> Dict[str, List[Dict]]:
        """Pre-authenticate sources for all poll offices"""
        self.stdout.write(self.style.NOTICE(f"Pre-authenticating sources... for {len(poll_offices)}"))

        # Get available sources
        available_sources = []
        i = 0
        async for source in Source.objects.all():
            available_sources.append(source)

            if i >= self.pre_auth_count:
                break
            else:
                i += 1
        self.stdout.write(self.style.NOTICE(f"Found {len(available_sources)} available sources"))
        # available_sources = list(await Source.objects.afilter()[:self.pre_auth_count])

        # Create authentication tasks
        auth_tasks = []
        semaphore = asyncio.Semaphore(self.concurrent)  # Limit concurrent requests

        async with aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=30),
                connector=aiohttp.TCPConnector(limit=self.concurrent * 2)
        ) as session:

            for poll_office in poll_offices:
                # Authenticate multiple sources per poll office
                sources_per_office = random.randint(2, 5)
                office_sources = available_sources[:sources_per_office]
                available_sources = available_sources[sources_per_office:]

                self.stdout.write(self.style.NOTICE(f"{sources_per_office=} {len(office_sources)=} {len(available_sources)=} available sources"))

                for source in office_sources:
                    if source.elector_id in self.credentials:
                        task = self.authenticate_source(
                            session, semaphore, source, poll_office
                        )
                        auth_tasks.append(task)

            # Execute all authentication requests
            auth_results = await asyncio.gather(*auth_tasks, return_exceptions=True)

        # Organize results by poll office
        authenticated_tokens = defaultdict(list)
        successful_auths = 0

        for result in auth_results:
            if isinstance(result, dict) and 'token' in result:
                authenticated_tokens[result['poll_office_id']].append(result)
                successful_auths += 1
            elif isinstance(result, Exception):
                if self.verbosity >= 2:
                    self.stdout.write(f"Auth exception: {result}")

        self.stdout.write(
            self.style.SUCCESS(f"✅ Successfully authenticated {successful_auths} sources")
        )

        return authenticated_tokens

    async def authenticate_source(
            self,
            session: aiohttp.ClientSession,
            semaphore: asyncio.Semaphore,
            source: Source,
            poll_office: PollOffice
    ) -> Optional[Dict]:
        """Authenticate a single source"""
        async with semaphore:
            payload = {
                "elector_id": source.elector_id,
                "password": self.credentials[source.elector_id],
                "poll_office_id": poll_office.identifier,
            }

            try:
                async with session.post(self.auth_url, json=payload) as response:
                    if response.status == 200:
                        data = await response.json()
                        if 'token' in data:
                            return {
                                'token': data['token'],
                                'source_id': source.elector_id,
                                'poll_office_id': poll_office.identifier
                            }

                    if self.verbosity >= 3:
                        error_text = await response.text()
                        self.stdout.write(
                            f"Auth failed for {source.elector_id}: {response.status} {error_text}"
                        )

            except Exception as e:
                if self.verbosity >= 2:
                    self.stdout.write(f"Auth error for {source.elector_id}: {e}")

        return None

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