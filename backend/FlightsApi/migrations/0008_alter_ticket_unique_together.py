# Generated by Django 4.2.1 on 2023-08-11 15:03

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('FlightsApi', '0007_rename_is_canceled_flight_is_cancelled_and_more'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='ticket',
            unique_together=set(),
        ),
    ]