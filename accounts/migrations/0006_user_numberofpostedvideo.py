# Generated by Django 5.1.2 on 2024-10-10 02:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0005_loginattempt'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='Numberofpostedvideo',
            field=models.IntegerField(default=0),
        ),
    ]
