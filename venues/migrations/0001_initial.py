# Generated by Django 4.2.7 on 2023-12-06 12:22

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('turf_owner', '0005_rename_owner_verfied_owners_owner_verified'),
    ]

    operations = [
        migrations.CreateModel(
            name='Venues',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('venue_name', models.CharField(max_length=100)),
                ('place', models.CharField(max_length=100)),
                ('city', models.CharField(max_length=100)),
                ('state', models.CharField(max_length=100)),
                ('address', models.TextField()),
                ('location', models.URLField()),
                ('about_venue', models.TextField()),
                ('opening_time', models.TimeField()),
                ('closing_time', models.TimeField()),
                ('created_at', models.DateField()),
                ('active', models.BooleanField()),
                ('venue_status', models.CharField(choices=[('requested', 'Requested'), ('accepted', 'Accepted'), ('rejected', 'Rejected')], max_length=20)),
                ('owner_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='turf_owner.owners')),
            ],
        ),
    ]
