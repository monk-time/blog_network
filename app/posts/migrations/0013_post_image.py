# Generated by Django 2.2.19 on 2023-02-22 09:34

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('posts', '0012_auto_20230130_1228'),
    ]

    operations = [
        migrations.AddField(
            model_name='post',
            name='image',
            field=models.ImageField(
                blank=True, upload_to='posts/', verbose_name='Картинка'
            ),
        ),
    ]
