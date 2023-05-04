# Generated by Django 3.1.3 on 2022-01-25 06:26

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0006_auto_20220125_1156'),
        ('user', '0002_auto_20220115_1206'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='talentuser',
            name='store_description',
        ),
        migrations.RemoveField(
            model_name='talentuser',
            name='store_logo',
        ),
        migrations.RemoveField(
            model_name='talentuser',
            name='store_name',
        ),
        migrations.CreateModel(
            name='Seller',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('store_name', models.CharField(blank=True, max_length=50)),
                ('store_description', models.TextField(blank=True)),
                ('store_logo', models.ImageField(blank=True, upload_to='media/store/logo/')),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('generaluser', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='seller', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='ProductWishlist',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('wishlist_of', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('wishlist_product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='store.product')),
            ],
        ),
    ]