# Generated by Django 2.2.10 on 2021-03-21 21:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0004_item_order'),
    ]

    operations = [
        migrations.AlterField(
            model_name='item_order',
            name='notes',
            field=models.TextField(default=''),
        ),
    ]