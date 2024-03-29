# Generated by Django 4.2.7 on 2023-11-30 09:03

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Owners',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('owner_name', models.CharField(max_length=100)),
                ('owner_email', models.EmailField(max_length=100, unique=True)),
                ('owner_phone', models.BigIntegerField(unique=True)),
                ('owner_password', models.CharField(max_length=100)),
            ],
        ),
    ]
