from django.core.management.base import BaseCommand
from allauth.socialaccount.models import SocialApp

class Command(BaseCommand):
    help = 'Setup social applications'

    def handle(self, *args, **options):
        SocialApp.objects.get_or_create(
            provider='google',
            defaults={
                'name': 'Google',
                'client_id': 'your-client-id',
                'secret': 'your-secret-key',
            }
        )
        self.stdout.write(self.style.SUCCESS('Social applications setup complete'))