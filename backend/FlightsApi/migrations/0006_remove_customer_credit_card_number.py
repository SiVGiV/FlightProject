# Generated by Django 4.2.1 on 2023-06-27 11:13

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('FlightsApi', '0005_rename_remaining_seats_flight_total_seats_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='customer',
            name='credit_card_number',
        ),
    ]