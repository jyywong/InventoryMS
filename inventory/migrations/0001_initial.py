# Generated by Django 2.2.10 on 2021-03-21 18:06

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Inventory',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name='Lab',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('members', models.ManyToManyField(to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Item',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('e_date', models.DateField()),
                ('manufacturer', models.CharField(max_length=255)),
                ('notes', models.TextField()),
                ('bar_code', models.BigIntegerField()),
                ('location_text', models.TextField()),
                ('quantity', models.IntegerField()),
                ('inventory', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='inventory', to='inventory.Inventory')),
            ],
        ),
        migrations.AddField(
            model_name='inventory',
            name='lab',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='lab', to='inventory.Lab'),
        ),
    ]