# Generated by Django 5.1 on 2024-10-02 03:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('forexJournal', '0007_strategymodel_market_conditions_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='strategymodel',
            name='dollar_value_risk',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=5, null=True),
        ),
        migrations.AddField(
            model_name='strategymodel',
            name='entry_criteria',
            field=models.CharField(blank=True, max_length=250, null=True),
        ),
        migrations.AddField(
            model_name='strategymodel',
            name='exit_criteria',
            field=models.CharField(blank=True, max_length=250, null=True),
        ),
    ]
