# Generated by Django 5.0 on 2024-01-11 15:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0002_note_mode_time'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='note',
            name='mode_time',
        ),
        migrations.AddField(
            model_name='note',
            name='mod_time',
            field=models.DateTimeField(default=None, null=True),
        ),
    ]
