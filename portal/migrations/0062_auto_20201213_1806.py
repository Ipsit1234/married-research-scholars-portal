# Generated by Django 3.0.7 on 2020-12-13 12:36

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('portal', '0061_auto_20201213_1725'),
    ]

    operations = [
        migrations.AddField(
            model_name='applicant',
            name='acad_details_verification_date',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
        migrations.AddField(
            model_name='applicant',
            name='acad_details_verified',
            field=models.BooleanField(default=False, editable=False),
        ),
        migrations.AlterField(
            model_name='applicant',
            name='department',
            field=models.CharField(help_text="For example, 'Electrical Engineering'", max_length=128),
        ),
    ]