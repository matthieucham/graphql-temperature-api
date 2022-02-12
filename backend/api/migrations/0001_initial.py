# Generated by Django 4.0.2 on 2022-02-12 22:13

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='TemperatureModel',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('timestamp', models.DateTimeField()),
                ('value', models.DecimalField(decimal_places=15, max_digits=18)),
            ],
        ),
    ]
