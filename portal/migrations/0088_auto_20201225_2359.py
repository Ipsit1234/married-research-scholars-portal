# Generated by Django 3.1.4 on 2020-12-25 18:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('portal', '0087_auto_20201225_1839'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='occupiedlist',
            options={'verbose_name': 'Occupied', 'verbose_name_plural': 'Occupied'},
        ),
        migrations.AlterModelOptions(
            name='vacatedlist',
            options={'verbose_name': 'Vacated', 'verbose_name_plural': 'Vacated'},
        ),
        migrations.AlterModelOptions(
            name='waitlist',
            options={'verbose_name': 'Offered', 'verbose_name_plural': 'Offered'},
        ),
        migrations.AlterField(
            model_name='applicant',
            name='acadsection_feedback',
            field=models.TextField(blank=True, default='', null=True, verbose_name='Feedback'),
        ),
    ]
