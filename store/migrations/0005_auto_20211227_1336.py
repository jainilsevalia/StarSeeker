# Generated by Django 3.1.3 on 2021-12-27 08:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0004_product_thumbnail'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='thumbnail',
            field=models.FileField(blank=True, null=True, upload_to='media/store/img/'),
        ),
    ]
