# Generated by Django 4.2.7 on 2023-11-06 17:44

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('politician', '0012_alter_community_deadline'),
    ]

    operations = [
        migrations.AlterField(
            model_name='community',
            name='deadline',
            field=models.DateTimeField(default=datetime.datetime(2023, 11, 13, 17, 44, 26, 6453, tzinfo=datetime.timezone.utc), editable=False),
        ),
    ]