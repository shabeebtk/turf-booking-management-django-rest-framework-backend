# Generated by Django 4.2.7 on 2023-12-29 06:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0005_user_google_user_id'),
    ]

    operations = [
        migrations.CreateModel(
            name='RazorPayment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('amount', models.DecimalField(decimal_places=2, max_digits=10)),
                ('provider_order_id', models.CharField(max_length=200)),
            ],
        ),
    ]
