# Generated by Django 4.2.7 on 2023-11-30 10:37

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('turf_owner', '0002_owners_owner_phone_verfied'),
    ]

    operations = [
        migrations.CreateModel(
            name='OwnerOtp',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('otp_type', models.CharField(choices=[('email', 'email'), ('phone', 'phone')], max_length=50)),
                ('otp', models.CharField(max_length=10)),
                ('owner_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='turf_owner.owners')),
            ],
        ),
    ]
