from django.core.management.base import BaseCommand
from allauth.socialaccount.models import SocialApp
from django.conf import settings
from django.contrib.sites.models import Site

class Command(BaseCommand):
    help = 'Setup social applications'

    def handle(self, *args, **options):
        # 既存の Google エントリを削除
        SocialApp.objects.filter(provider='google').delete()

        # SITE_ID = 1 以外の Site を削除
        Site.objects.exclude(id=settings.SITE_ID).delete()

        # SITE_ID = 1 の Site をデフォルト（example.com）に設定
        site, created = Site.objects.get_or_create(id=settings.SITE_ID)
        site.domain = 'example.com'
        site.name = 'example.com'
        site.save()

        # 新しい SocialApp を作成
        app = SocialApp.objects.create(
            provider='google',
            name='Google',
            client_id=settings.GOOGLE_CLIENT_ID,
            secret=settings.GOOGLE_SECRET_KEY,
        )
        app.sites.add(site)
        self.stdout.write(self.style.SUCCESS(f'Successfully registered SocialApp: {app}'))
        self.stdout.write(self.style.SUCCESS(f'Successfully updated Site: {site}'))