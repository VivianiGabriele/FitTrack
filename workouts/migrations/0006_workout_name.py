# Generated by Django 5.2.1 on 2025-07-07 22:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('workouts', '0005_alter_workout_options_alter_workout_date_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='workout',
            name='name',
            field=models.CharField(default='Allenamento', max_length=100, verbose_name='Nome allenamento'),
        ),
    ]
