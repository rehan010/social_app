# Generated by Django 2.2.6 on 2019-12-25 05:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('web_portal', '0003_auto_20191222_0954'),
    ]

    operations = [
        migrations.AlterField(
            model_name='post',
            name='image',
            field=models.ImageField(default=None, null=True, upload_to='post_images/%Y/%m/%d'),
        ),
    ]
