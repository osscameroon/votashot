from django.apps import AppConfig
from django.db.utils import ProgrammingError


class CoreConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "core"

    def ready(self):
        self.create_default_candidate_parties_if_needed()
        self.load_poll_offices_if_empty()
        self.load_candidate_parties_if_empty()

    def create_default_candidate_parties_if_needed(self):
        from core.models import CandidateParty
        try:
            CandidateParty.objects.get_or_create(
                identifier="**undecided**",
                party_name="UNDECIDED",
                candidate_name="UNDECIDED",
            )

            CandidateParty.objects.get_or_create(
                identifier="**white**",
                party_name="WHITE",
                candidate_name="WHITE",
            )
        except ProgrammingError:
            pass

    def load_poll_offices_if_empty(self):
        """If there is not PollOffice in the database load the poll_offices.json
        located inside settings.BASE_DIR folder"""
        from django.conf import settings
        from django.db import transaction
        import json
        from pathlib import Path

        try:
            from core.models import PollOffice
        except ProgrammingError:
            # Migrations not yet applied in some contexts
            return

        try:
            if PollOffice.objects.exists():
                return

            base_dir = Path(getattr(settings, "BASE_DIR", Path.cwd()))
            downloads_dir = Path(getattr(settings, "DOWNLOADS_DIR", base_dir / "downloads"))

            candidates = [
                base_dir / "poll_offices.json",
                downloads_dir / "poll_offices.json",
            ]
            json_path = next((p for p in candidates if p.exists()), None)
            if not json_path:
                return

            with json_path.open("r", encoding="utf-8") as f:
                data = json.load(f)

            if not isinstance(data, list):
                return

            instances = []
            for item in data:
                if not isinstance(item, dict):
                    continue
                name = item.get("name")
                identifier = item.get("identifier")
                if not name or not identifier:
                    continue
                country = item.get("country") or "Unknown"
                instances.append(
                    PollOffice(
                        name=name,
                        identifier=str(identifier),
                        country=str(country),
                        state=item.get("state") or None,
                        region=item.get("region") or None,
                        city=item.get("city") or None,
                        county=item.get("county") or None,
                        district=item.get("district") or None,
                        voters_count=item.get("voters_count") or None,
                    )
                )

            if not instances:
                return

            with transaction.atomic():
                PollOffice.objects.bulk_create(instances, ignore_conflicts=True)
        except ProgrammingError:
            # Tables may not be ready; ignore during initial migrate/setup
            return
        except Exception:
            # Be silent on ready() to avoid breaking startup
            return

    def load_candidate_parties_if_empty(self):
        """If there is not PollOffice in the database load the poll_offices.json
        located inside settings.BASE_DIR folder"""
        from django.conf import settings
        from django.db import transaction
        import json
        from pathlib import Path

        try:
            from core.models import CandidateParty
        except ProgrammingError:
            # Migrations not yet applied in some contexts
            return

        try:
            if CandidateParty.objects.count() > 2:
                return

            with (settings.BASE_DIR / "candidate_parties.json").open() as fp:
                candidates = json.load(fp)

            rows = []
            for candidate in candidates:
                rows.append(CandidateParty(**candidate))

            CandidateParty.objects.bulk_create(rows)
            print(f"Created {len(rows)} CandidateParty objects.")
        except ProgrammingError:
            pass
        except Exception as e:
            print(e)
