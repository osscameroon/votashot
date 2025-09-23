from django.apps import AppConfig
from django.db.utils import ProgrammingError


class CoreConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "core"

    def ready(self):
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
