# Generated by Django 5.1 on 2024-11-18 17:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('forexJournal', '0013_alter_tradesmodel_lot_size_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tradesmodel',
            name='commission_usd',
            field=models.DecimalField(decimal_places=4, max_digits=8),
        ),
        migrations.AlterField(
            model_name='tradesmodel',
            name='swap_usd',
            field=models.DecimalField(decimal_places=3, max_digits=8),
        ),
        migrations.AlterField(
            model_name='tradesmodel',
            name='symbol',
            field=models.CharField(max_length=20),
        ),
    ]
