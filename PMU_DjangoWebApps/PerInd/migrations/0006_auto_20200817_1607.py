# Generated by Django 2.2.14 on 2020-08-17 20:07

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('PerInd', '0005_merge_20200731_1431'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='indicatordata',
            options={'managed': False, 'ordering': ['indicator__indicator_title', 'year_month__yyyy', 'year_month__mm']},
        ),
    ]
