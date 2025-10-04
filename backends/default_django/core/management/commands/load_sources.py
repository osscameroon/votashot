from __future__ import annotations

import json

from django.conf import settings

from django.core.management.base import BaseCommand
from django.db import transaction
from faker import Faker

from core.enums import SourceType
from core.models import Source, User


class Command(BaseCommand):
    help = "Create fake Source entries using Faker with proper password hashing."

    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):
        self.stdout.write(
            self.style.NOTICE(
                "Loading fake Source entries...",
            )
        )
        with (settings.BASE_DIR / "sources.json").open() as fp:
            sources_data = json.load(fp)

        to_create = len(sources_data)
        users_tmp = [User(username=f"username-s{i+1}", is_active=True) for i in range(to_create)]
        users = User.objects.bulk_create(users_tmp)
        self.stdout.write(
            self.style.NOTICE(
                "Created users"
            )
        )

        sources_tmp = [Source(
            elector_id=sources_data[i]['fields']['elector_id'],
            password=sources_data[i]['fields']['password'],
            type=sources_data[i]['fields']['type'],
            official_org=sources_data[i]['fields']['official_org'],
            full_name=sources_data[i]['fields']['full_name'],
            email=sources_data[i]['fields']['email'],
            phone_number=sources_data[i]['fields']['phone_number'],
            user_id=users[i].id
        )

                       for i in range(to_create)]
        Source.objects.bulk_create(sources_tmp)
        self.stdout.write(
            self.style.NOTICE(
                "Created sources. Done!"
            )
        )
