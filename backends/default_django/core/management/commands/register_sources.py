from __future__ import annotations

import asyncio
import aiohttp
import csv
import json
import os
import random
from collections import defaultdict
from typing import Dict, List, Optional, Tuple
import logging
import time

from django.core.management.base import BaseCommand

from core.models import PollOffice, Source


class Command(BaseCommand):
    help = (
        "Register sources per poll office by authenticating 1-5 random sources "
        "asynchronously and persisting responses to source_tokens.json"
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--server-url",
            type=str,
            default="http://localhost:8448",
            help="Base server URL (default: http://localhost:8448)",
        )
        parser.add_argument(
            "--concurrent",
            type=int,
            default=200,
            help="Max concurrent HTTP requests (default: 200)",
        )
        parser.add_argument(
            "--timeout",
            type=int,
            default=30,
            help="Total request timeout in seconds (default: 30)",
        )
        parser.add_argument(
            "--output",
            type=str,
            default="source_tokens.json",
            help="Output JSON filename (default: source_tokens.json)",
        )

    def handle(self, *args, **options):
        # Logger setup (respects Django logging config if present)
        self.logger = logging.getLogger(__name__)
        if int(options.get("verbosity", 1)) >= 2:
            self.logger.setLevel(logging.DEBUG)
        else:
            self.logger.setLevel(logging.INFO)

        self.server_url = options["server_url"].rstrip("/")
        self.auth_url = f"{self.server_url}/api/authenticate/"
        self.concurrent = int(options["concurrent"]) or 1
        self.timeout = int(options["timeout"]) or 30
        self.output = options["output"]
        self.verbosity = int(options.get("verbosity", 1))

        # 1) Load and shuffle all sources
        sources: List[Source] = list(Source.objects.all())
        random.shuffle(sources)

        if not sources:
            self.stdout.write(self.style.WARNING("No Source records found."))
            return

        # 2) Load credentials from sources.csv (format: elector_id,password)
        creds = self._load_credentials()
        if not creds:
            self.stdout.write(self.style.WARNING("No credentials loaded from sources.csv."))

        # 3) Fetch all poll offices (only identifier is needed)
        poll_offices: List[PollOffice] = list(PollOffice.objects.all())
        if not poll_offices:
            self.stdout.write(self.style.WARNING("No PollOffice records found."))
            return

        self.stdout.write(
            self.style.NOTICE(
                f"Preparing registration for {len(poll_offices)} poll offices "
                f"using {len(sources)} sources (concurrency={self.concurrent})"
            )
        )
        self.logger.info(
            "register_sources starting | offices=%d sources=%d server=%s",
            len(poll_offices), len(sources), self.server_url,
        )

        # 4) Build async tasks: for each office, authenticate 1-5 sources (pop from list)
        #    Keep track of which office the task belongs to.
        tasks: List[asyncio.Task] = []
        semaphore = asyncio.Semaphore(self.concurrent)

        async def runner():
            connector = aiohttp.TCPConnector(limit=self.concurrent * 2)
            timeout = aiohttp.ClientTimeout(total=self.timeout)
            async with aiohttp.ClientSession(connector=connector, timeout=timeout) as session:
                # Plan all requests first to know total for progress
                planned: List[Tuple[str, Dict[str, str]]] = []
                skipped_no_creds = 0
                exhausted_at_office = None
                for idx, office in enumerate(poll_offices):
                    sources_for_pof = random.randint(1, 5)
                    for _ in range(sources_for_pof):
                        if not sources:
                            exhausted_at_office = idx
                            break
                        src = sources.pop()
                        password = creds.get(src.elector_id)
                        if not password:
                            skipped_no_creds += 1
                            continue
                        payload = {
                            "poll_office_id": office.identifier,
                            "elector_id": src.elector_id,
                            "password": password,
                        }
                        planned.append((office.identifier, payload))
                    if exhausted_at_office is not None:
                        break

                total = len(planned)
                self.logger.info(
                    "planned auth requests=%d | skipped_no_creds=%d | exhausted_at_office=%s",
                    total,
                    skipped_no_creds,
                    exhausted_at_office if exhausted_at_office is not None else "-",
                )
                self.stdout.write(self.style.NOTICE(f"Planned {total} auth requests"))

                # Create tasks
                for office_id, payload in planned:
                    tasks.append(
                        asyncio.create_task(
                            self._authenticate(session, semaphore, office_id, payload)
                        )
                    )

                # Progress monitor
                results: Dict[str, List[dict]] = defaultdict(list)
                completed = 0
                errors = 0
                start_time = time.time()

                async def monitor():
                    last_completed = 0
                    while completed < total:
                        await asyncio.sleep(2)
                        elapsed = time.time() - start_time
                        delta = completed - last_completed
                        rate = delta / 2 if elapsed > 0 else 0
                        percent = (completed / total) * 100 if total else 100
                        self.stdout.write(
                            f"Progress: {completed}/{total} ({percent:.1f}%) - {rate:.0f} req/s"
                        )
                        last_completed = completed

                monitor_task = asyncio.create_task(monitor())

                # Execute tasks and collate results
                try:
                    for coro in asyncio.as_completed(tasks):
                        office_id, resp_obj = await coro
                        if resp_obj is not None:
                            results[office_id].append(resp_obj)
                        else:
                            errors += 1
                        completed += 1
                        if self.verbosity >= 3 and completed % 500 == 0:
                            self.logger.debug("completed=%d/%d errors=%d", completed, total, errors)
                finally:
                    monitor_task.cancel()
                    try:
                        await monitor_task
                    except asyncio.CancelledError:
                        pass

                elapsed_total = time.time() - start_time
                self.logger.info(
                    "auth finished | completed=%d total=%d errors=%d elapsed=%.2fs",
                    completed, total, errors, elapsed_total,
                )
                self.stdout.write(
                    self.style.SUCCESS(
                        f"Completed {completed}/{total} auth requests in {elapsed_total:.2f}s (errors={errors})"
                    )
                )

                return results

        # 5) Run the async workflow and write outputs
        try:
            results = asyncio.run(runner())
        except KeyboardInterrupt:
            self.stdout.write(self.style.WARNING("Interrupted by user."))
            return

        # 6) Persist results to JSON
        try:
            with open(self.output, "w", encoding="utf-8") as f:
                json.dump(results, f, ensure_ascii=False)
            self.stdout.write(self.style.SUCCESS(f"Saved results to {self.output}"))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Failed to write {self.output}: {e}"))

    def _load_credentials(self) -> Dict[str, str]:
        creds_path = os.path.join(os.getcwd(), "sources.csv")
        credentials: Dict[str, str] = {}
        if not os.path.exists(creds_path):
            return credentials
        try:
            with open(creds_path, newline="", encoding="utf-8") as f:
                reader = csv.reader(f)
                header = next(reader, None)
                for row in reader:
                    if len(row) >= 2:
                        elector_id, password = row[0], row[1]
                        credentials[elector_id] = password
        except Exception:
            # Return whatever we have (possibly empty) to avoid crashing
            pass
        return credentials

    async def _authenticate(
        self,
        session: aiohttp.ClientSession,
        semaphore: asyncio.Semaphore,
        office_identifier: str,
        payload: Dict[str, str],
    ) -> Tuple[str, Optional[dict]]:
        async with semaphore:
            try:
                async with session.post(self.auth_url, json=payload) as resp:
                    # Try to parse JSON; if it fails, fall back to status/text
                    try:
                        data = await resp.json()
                    except Exception:
                        text = await resp.text()
                        data = {"status": resp.status, "body": text}
                    return office_identifier, data
            except Exception as e:
                if self.verbosity >= 2:
                    self.stdout.write(f"Auth error for {payload.get('elector_id')}: {e}")
                return office_identifier, None
