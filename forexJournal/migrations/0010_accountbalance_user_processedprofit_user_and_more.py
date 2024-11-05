# Generated by Django 5.1 on 2024-11-05 09:36

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('forexJournal', '0009_mt5login_profile'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='accountbalance',
            name='user',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='account_balance', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='processedprofit',
            name='user',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='strategymodel',
            name='user',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='strategies', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='tradesmodel',
            name='user',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='trades', to=settings.AUTH_USER_MODEL),
        ),
    ]
