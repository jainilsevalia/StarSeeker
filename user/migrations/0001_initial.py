# Generated by Django 3.1.3 on 2021-12-16 17:13

import ckeditor.fields
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import multiselectfield.db.fields


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='GeneralUser',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('email', models.EmailField(max_length=70, unique=True)),
                ('name', models.CharField(max_length=50)),
                ('userlink', models.SlugField(blank=True, null=True)),
                ('phone_number', models.CharField(blank=True, max_length=15, verbose_name='phone number')),
                ('profile_picture', models.ImageField(blank=True, null=True, upload_to='media/generalprofile/img')),
                ('is_verified', models.BooleanField(default=False)),
                ('date_created', models.DateTimeField(auto_now_add=True)),
                ('last_login', models.DateTimeField(blank=True, null=True)),
                ('is_admin', models.BooleanField(default=False)),
                ('is_staff', models.BooleanField(default=False)),
                ('is_active', models.BooleanField(default=True)),
                ('is_superuser', models.BooleanField(default=False)),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.Group', verbose_name='groups')),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.Permission', verbose_name='user permissions')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='State',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(blank=True, max_length=30)),
            ],
        ),
        migrations.CreateModel(
            name='TalentUser',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_kyc_done', models.BooleanField(default=False)),
                ('price', models.DecimalField(blank=True, decimal_places=2, max_digits=10)),
                ('description', ckeditor.fields.RichTextField(blank=True)),
                ('achievements', models.TextField(blank=True)),
                ('thumbnail', models.ImageField(blank=True, upload_to='media/talentprofile/img/thumbnail')),
                ('gender', models.CharField(max_length=20)),
                ('secondary_skills', models.CharField(blank=True, max_length=50)),
                ('engagement', models.CharField(max_length=20)),
                ('is_trained', models.BooleanField()),
                ('availability', multiselectfield.db.fields.MultiSelectField(choices=[('Monday', 'Monday'), ('Tuesday', 'Tuesday'), ('Wednesday', 'Wednesday'), ('Thursday', 'Thursday'), ('Friday', 'Friday'), ('Saturday', 'Saturday'), ('Sunday', 'Sunday')], max_length=56)),
                ('will_travel', models.BooleanField()),
                ('provide_training', models.BooleanField()),
                ('generaluser', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='talentuser', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Wishlist',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('wishlist_of', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('wishlist_profile', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='user.talentuser')),
            ],
        ),
        migrations.CreateModel(
            name='UserLogin',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('timestamp', models.DateTimeField()),
                ('generaluser', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='TalentVideo',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('video', models.FileField(blank=True, upload_to='media/talentprofile/video')),
                ('video_order', models.IntegerField(blank=True, default=0)),
                ('upload_date', models.DateTimeField(auto_now_add=True)),
                ('talentuser', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='user.talentuser')),
            ],
        ),
        migrations.CreateModel(
            name='TalentImage',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image', models.ImageField(blank=True, null=True, upload_to='media/talentprofile/img/content')),
                ('image_order', models.IntegerField(blank=True, default=0)),
                ('upload_date', models.DateTimeField(auto_now_add=True)),
                ('talentuser', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='user.talentuser')),
            ],
        ),
        migrations.CreateModel(
            name='OtherCountry',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('address', models.CharField(blank=True, max_length=150)),
                ('state', models.CharField(max_length=50)),
                ('city', models.CharField(max_length=50)),
                ('pincode', models.CharField(blank=True, max_length=15)),
                ('is_default', models.BooleanField(default=False)),
                ('generaluser', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='FAQ',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('question', models.CharField(blank=True, max_length=250)),
                ('answer', models.CharField(blank=True, max_length=250)),
                ('upload_date', models.DateTimeField(auto_now_add=True)),
                ('talentuser', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='user.talentuser')),
            ],
        ),
        migrations.CreateModel(
            name='EmbeddedVideo',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('embed_video_url', models.CharField(blank=True, max_length=500)),
                ('upload_date', models.DateTimeField(auto_now_add=True)),
                ('talentuser', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='user.talentuser')),
            ],
        ),
        migrations.CreateModel(
            name='City',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(blank=True, max_length=30)),
                ('state', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='user.state')),
            ],
        ),
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
                ('talentuser', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='user.talentuser')),
            ],
        ),
        migrations.CreateModel(
            name='Address',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('address', models.CharField(blank=True, max_length=150)),
                ('pincode', models.CharField(blank=True, max_length=15)),
                ('is_default', models.BooleanField(default=False)),
                ('city', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='user.city')),
                ('generaluser', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('state', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='user.state')),
            ],
        ),
    ]
