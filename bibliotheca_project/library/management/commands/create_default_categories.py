from django.core.management.base import BaseCommand
from library.models import Category


class Command(BaseCommand):
    help = 'Create default book categories'

    def handle(self, *args, **kwargs):
        categories = [
            {'name': 'Roman', 'description': 'Romans et littérature fiction'},
            {'name': 'Science-fiction', 'description': 'Livres de science-fiction'},
            {'name': 'Fantastique', 'description': 'Livres fantastiques'},
            {'name': 'Policier', 'description': 'Romans policiers et thrillers'},
            {'name': 'Histoire', 'description': 'Livres d\'histoire'},
            {'name': 'Science', 'description': 'Livres scientifiques'},
            {'name': 'Philosophie', 'description': 'Ouvrages philosophiques'},
            {'name': 'Biographie', 'description': 'Biographies et autobiographies'},
            {'name': 'Jeunesse', 'description': 'Livres pour enfants et adolescents'},
            {'name': 'Bande dessinée', 'description': 'Bandes dessinées et comics'},
            {'name': 'Poésie', 'description': 'Recueils de poésie'},
            {'name': 'Théâtre', 'description': 'Pièces de théâtre'},
        ]

        created_count = 0
        for cat_data in categories:
            category, created = Category.objects.get_or_create(
                name=cat_data['name'],
                defaults={'description': cat_data['description']}
            )
            if created:
                created_count += 1
                self.stdout.write(f'Created category: {category.name}')
            else:
                self.stdout.write(f'Category already exists: {category.name}')

        self.stdout.write(self.style.SUCCESS(f'Successfully created {created_count} categories'))
