# Generated by Django 2.2.7 on 2019-11-21 11:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('chat', '0002_auto_20191120_1404'),
    ]

    operations = [
        migrations.AlterField(
            model_name='chat',
            name='participants',
            field=models.ManyToManyField(blank=True, related_name='chats', to='chat.Contact'),
        ),
    ]
