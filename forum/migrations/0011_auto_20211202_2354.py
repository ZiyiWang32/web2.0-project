# Generated by Django 3.2.9 on 2021-12-02 23:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('forum', '0010_auto_20211202_2348'),
    ]

    operations = [
        migrations.AlterField(
            model_name='favorite',
            name='topic_text',
            field=models.CharField(max_length=50),
        ),
        migrations.AlterField(
            model_name='like',
            name='topic_text',
            field=models.CharField(max_length=50),
        ),
        migrations.AlterField(
            model_name='post',
            name='content_text',
            field=models.CharField(max_length=200),
        ),
        migrations.AlterField(
            model_name='post',
            name='topic_text',
            field=models.CharField(max_length=50),
        ),
        migrations.AlterField(
            model_name='response',
            name='text',
            field=models.CharField(max_length=200),
        ),
    ]
