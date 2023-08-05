# Generated by Django 4.2.1 on 2023-06-21 13:02

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('FlightsApi', '0001_squashed_0004_alter_airlinecompany_options_alter_country_options_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='flight',
            old_name='remaining_seats',
            new_name='total_seats',
        ),
        migrations.AddField(
            model_name='flight',
            name='is_canceled',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='ticket',
            name='is_canceled',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='airlinecompany',
            name='country',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='airlines', to='FlightsApi.country'),
        ),
    ]
