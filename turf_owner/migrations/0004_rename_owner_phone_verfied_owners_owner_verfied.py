# Generated by Django 4.2.7 on 2023-11-30 11:56

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('turf_owner', '0003_ownerotp'),
    ]

    operations = [
        migrations.RenameField(
            model_name='owners',
            old_name='owner_phone_verfied',
            new_name='owner_verfied',
        ),
    ]
