# Generated by Django 2.2.16 on 2023-03-21 16:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0013_auto_20230321_1944'),
    ]

    operations = [
        migrations.AlterField(
            model_name='group',
            name='description',
            field=models.TextField(help_text='Группа, к которой будет относиться пост', verbose_name='Группа'),
        ),
    ]
