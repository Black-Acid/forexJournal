# Generated by Django 5.1 on 2024-11-18 18:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('forexJournal', '0014_alter_tradesmodel_commission_usd_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tradesmodel',
            name='profit_usd',
            field=models.DecimalField(decimal_places=3, max_digits=20),
        ),
    ]
