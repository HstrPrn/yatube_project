# Generated by Django 2.2.19 on 2023-02-08 21:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0002_auto_20230208_0100'),
    ]

    operations = [
        migrations.AlterField(
            model_name='group',
            name='description',
            field=models.CharField(max_length=50),
        ),
        migrations.AlterField(
            model_name='group',
            name='title',
            field=models.CharField(max_length=30),
        ),
    ]
