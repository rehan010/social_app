# Generated by Django 2.2.6 on 2019-12-25 09:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('web_portal', '0004_auto_20191225_0521'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='type',
            field=models.CharField(choices=[('1', 'BA'), ('2', 'Sup'), ('3', 'Man'), ('4', 'Exec'), ('5', 'Client')], default='BA', max_length=10),
        ),
    ]