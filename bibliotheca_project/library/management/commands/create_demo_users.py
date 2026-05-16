from django.core.management.base import BaseCommand
from library.models import User


class Command(BaseCommand):
    help = 'Crée des comptes démo : étudiant, bibliothécaire et administrateur'

    def handle(self, *args, **options):
        demos = [
            {
                'username': 'etudiant',
                'password': 'demo12345',
                'email': 'etudiant@demo.fr',
                'first_name': 'Jean',
                'last_name': 'Dupont',
                'user_type': 'member',
            },
            {
                'username': 'bibliothecaire',
                'password': 'demo12345',
                'email': 'biblio@demo.fr',
                'first_name': 'Marie',
                'last_name': 'Martin',
                'user_type': 'librarian',
            },
            {
                'username': 'admin',
                'password': 'demo12345',
                'email': 'admin@demo.fr',
                'first_name': 'Paul',
                'last_name': 'Admin',
                'user_type': 'admin',
                'is_staff': True,
                'is_superuser': True,
            },
        ]

        for data in demos:
            username = data['username']
            password = data.pop('password')
            is_staff = data.pop('is_staff', False)
            is_superuser = data.pop('is_superuser', False)

            user, created = User.objects.get_or_create(username=username, defaults=data)
            user.set_password(password)
            user.is_staff = is_staff
            user.is_superuser = is_superuser
            for key, value in data.items():
                setattr(user, key, value)
            user.save()

            action = 'Créé' if created else 'Mis à jour'
            self.stdout.write(self.style.SUCCESS(f'{action} : {username} / {password} ({user.user_type})'))

        self.stdout.write(self.style.WARNING('\nConnectez-vous sur /login/ pour tester les 3 interfaces.'))
