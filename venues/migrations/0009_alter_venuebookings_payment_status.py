# Generated by Django 4.2.7 on 2023-12-26 06:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('venues', '0008_alter_venuefacilities_venue_id_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='venuebookings',
            name='payment_status',
            field=models.BooleanField(default=False),
        ),
    ]
