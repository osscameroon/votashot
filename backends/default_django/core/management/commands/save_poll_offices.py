from __future__ import annotations

import json
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand

from core.models import PollOffice
from core.serializers import PollOfficeSerializer


class Command(BaseCommand):
    help = (
        "Serialize all PollOffice records using PollOfficeSerializer and "
        "save them to poll_offices.json"
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--output",
            "-o",
            type=str,
            default=None,
            help=(
                "Output file path. Defaults to BASE_DIR/poll_offices.json "
                "if not provided."
            ),
        )
        parser.add_argument(
            "--indent",
            type=int,
            default=2,
            help="JSON indentation (default: 2)",
        )

    def handle(self, *args, **options):
        # Resolve output path
        base_dir: Path = Path(getattr(settings, "BASE_DIR", Path.cwd()))
        output_opt: str | None = options.get("output")
        output_path = Path(output_opt) if output_opt else base_dir / "poll_offices.json"

        # Fetch and serialize poll offices deterministically
        queryset = PollOffice.objects.all().order_by("identifier", "id")
        serializer = PollOfficeSerializer(queryset, many=True)
        data = serializer.data

        # Write JSON file
        indent = int(options.get("indent") or 2)
        with output_path.open("w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=indent)

        self.stdout.write(
            self.style.SUCCESS(
                f"Saved {len(data)} poll offices to {output_path}"
            )
        )

