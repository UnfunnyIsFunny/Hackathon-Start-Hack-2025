import time
from django.core.management.base import BaseCommand
import sys
import subprocess
sys.path.append('..')
from .backend import fetch_data, process_data 
import asyncio

class Command(BaseCommand):
    help = 'Runs the activate method on my static service object'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Starting my service...'))
        try:
            while True:
                # This is where your long-running method is called
                fetch_data.load_keywords()
                fetch_data.fetch_specific()
                asyncio.run(process_data.main())
                time.sleep(3600)

            
        except KeyboardInterrupt:
            self.stdout.write(self.style.WARNING('Service stopped by user.'))