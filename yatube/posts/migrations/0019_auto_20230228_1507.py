# Generated by Django 2.2.19 on 2023-02-28 12:07

from django.db import migrations, models
import django.db.models.expressions


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0018_auto_20230224_1221'),
    ]

    operations = [
        migrations.AddConstraint(
            model_name='follow',
            constraint=models.CheckConstraint(check=models.Q(_negated=True, user=django.db.models.expressions.F('author')), name='cant_subscribe_to_self'),
        ),
    ]
