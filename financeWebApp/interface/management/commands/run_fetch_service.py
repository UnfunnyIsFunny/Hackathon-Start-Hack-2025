import time
from django.core.management.base import BaseCommand
import sys
import subprocess
sys.path.append('..')
sys.path.append('...')
from .backend import fetch_data, process_data 
from ... import models
import asyncio

class Command(BaseCommand):
    help = 'Runs the activate method on my static service object'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Starting my service...'))
        try:
            while True:
                fetch_data.load_keywords()
                fetch_data.fetch_specific()
                fetch_data.fetch_sec_filings()
                for portfolio in models.Portfolio.objects.all():
                    asyncio.run(process_data.main(portfolio))
                time.sleep(3600)
        except KeyboardInterrupt:
            self.stdout.write(self.style.WARNING('Service stopped by user.'))