# Generated by Django 5.1 on 2024-11-08 14:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('forexJournal', '0011_alter_mt5login_user'),
    ]

    operations = [
        migrations.AlterField(
            model_name='mt5login',
            name='login',
            field=models.CharField(max_length=100),
        ),
    ]
