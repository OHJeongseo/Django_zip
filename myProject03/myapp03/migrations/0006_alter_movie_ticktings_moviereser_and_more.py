# Generated by Django 4.0 on 2021-12-22 02:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myapp03', '0005_movie_ticktings'),
    ]

    operations = [
        migrations.AlterField(
            model_name='movie_ticktings',
            name='movieReser',
            field=models.DecimalField(decimal_places=1, default=0, max_digits=3),
        ),
        migrations.AlterField(
            model_name='movie_ticktings',
            name='moviegrade',
            field=models.DecimalField(decimal_places=1, default=0, max_digits=3),
        ),
    ]