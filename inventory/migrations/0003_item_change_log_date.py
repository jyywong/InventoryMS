# Generated by Django 2.2.10 on 2021-03-21 20:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0002_item_change_log'),
    ]

    operations = [
        migrations.AddField(
            model_name='item_change_log',
            name='date',
            field=models.DateTimeField(auto_now=True),
        ),
    ]
