# Generated by Django 3.1.3 on 2022-01-15 06:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='talentuser',
            name='store_description',
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name='talentuser',
            name='store_logo',
            field=models.ImageField(blank=True, upload_to='media/store/logo/'),
        ),
        migrations.AddField(
            model_name='talentuser',
            name='store_name',
            field=models.CharField(blank=True, max_length=50),
        ),
    ]
