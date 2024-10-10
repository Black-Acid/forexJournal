# Generated by Django 5.1 on 2024-09-10 15:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('forexJournal', '0002_accountbalance'),
    ]

    operations = [
        migrations.AddField(
            model_name='accountbalance',
            name='profits',
            field=models.DecimalField(decimal_places=2, default=0.0, max_digits=10),
        ),
    ]
