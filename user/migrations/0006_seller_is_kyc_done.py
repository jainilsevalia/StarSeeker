# Generated by Django 3.1.3 on 2022-02-10 17:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0005_auto_20220131_1940'),
    ]

    operations = [
        migrations.AddField(
            model_name='seller',
            name='is_kyc_done',
            field=models.BooleanField(default=False),
        ),
    ]