# Generated by Django 4.2.7 on 2024-01-03 06:46

from django.db import migrations, models

class Migration(migrations.Migration):

    dependencies = [
        ('app_admin', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='usernotification',
            name='date',
            field=models.DateTimeField(auto_now_add=True, default='2024-01-03'),
            preserve_default=False,
        ),
    ]