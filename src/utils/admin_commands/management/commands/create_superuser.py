from django.contrib.auth.models import User
from django.core.management.base import BaseCommand

from src.apps.authentication.mgmt.models import AdminToken


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('--username')
        parser.add_argument('--password')

    def handle(self, *args, **options):
        username = options['username']
        password = options['password']
        email = 'bigrussian@boss.com'
        user = User.objects.filter(email=email)
        if user:
            # smth is wrong with cascades
            AdminToken.objects.filter(user=user).delete()
            user.delete()

        User.objects.create_superuser(username, email, password)
