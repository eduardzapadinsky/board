# Generated by Django 4.1.7 on 2023-04-07 15:34

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0006_token'),
    ]

    operations = [
        migrations.DeleteModel(
            name='Token',
        ),
    ]