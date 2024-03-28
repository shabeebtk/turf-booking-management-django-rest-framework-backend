# Generated by Django 4.2.7 on 2024-01-11 10:43

from django.conf import settings
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('game', '0007_usergames_expired'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='gameusers',
            unique_together={('game_id', 'user_id')},
        ),
    ]