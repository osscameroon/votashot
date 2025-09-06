from django.apps import AppConfig


class CoreConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "core"

    def ready(self):
        from core.models import CandidateParty

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
