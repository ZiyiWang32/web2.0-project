# Generated by Django 3.2.9 on 2021-11-25 19:51

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('forum', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('user_name', models.CharField(max_length=10)),
                ('user_password', models.CharField(max_length=20)),
                ('user_level', models.IntegerField(default=0)),
                ('user_exp', models.IntegerField(default=0)),
                ('user_likeNum', models.IntegerField(default=0)),
                ('use_favoritesNum', models.IntegerField(default=0)),
            ],
        ),
    ]