import time

from django.core.management.base import BaseCommand
from django.db.utils import OperationalError
from django.db import connections


class Command(BaseCommand):
    """Django command to pause execution when database is unavailable"""

    def handle(self, *args, **options):
        self.stdout.write("Waiting for database...")
        db_conn = None
        while not db_conn:
            try:
                db_conn = connections['default']
            except OperationalError:
                self.stdout.write("Database unavailable, Waiting for 1 sec")
                time.sleep(1)

        self.stdout.write(self.style.SUCCESS('Database available'))
