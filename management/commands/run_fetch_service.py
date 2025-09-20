import time
from django.core.management.base import BaseCommand
import sys
import subprocess
sys.path.append('..')
from ..backend import fetch_data, process_data
class Command(BaseCommand):
    help = 'Runs the activate method on my static service object'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Starting my service...'))
        try:
            # This is where your long-running method is called
            fetch_data.load_keywords()
            fetch_data.fetch_specific()
            subprocess.Popen([sys.executable, 'process_data.py'], cwd='../backend')

            
        except KeyboardInterrupt:
            self.stdout.write(self.style.WARNING('Service stopped by user.'))