# Generated manually for 30-second borrowing demo

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('library', '0005_alter_author_options_alter_borrowing_unique_together_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='borrowing',
            name='due_date',
            field=models.DateTimeField(),
        ),
    ]
