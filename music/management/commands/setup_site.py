from django.core.management.base import BaseCommand
from django.contrib.sites.models import Site

class Command(BaseCommand):
    help = 'Sets up the default site domain and name'

    def handle(self, *args, **options):
        site = Site.objects.get(id=1)
        site.domain = 'junctify.onrender.com'
        site.name = 'Junctify'
        site.save()
        self.stdout.write(self.style.SUCCESS('Successfully updated site domain and name'))