# Generated by Django 2.2.10 on 2021-03-22 20:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0005_auto_20210321_1740'),
    ]

    operations = [
        migrations.AddField(
            model_name='item_order',
            name='status',
            field=models.CharField(choices=[('Pending', 'Pending'), ('Approved', 'Approved'), ('Rejected', 'Rejected')], default='Pending', max_length=100),
        ),
    ]