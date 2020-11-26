# Generated by Django 2.2.14 on 2020-11-26 09:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('FleetDataCollection', '0003_nyc_dotr_unit_main'),
    ]

    operations = [
        migrations.CreateModel(
            name='TblWorkUnitDivisionJoeSubs',
            fields=[
                ('id', models.AutoField(db_column='ID', primary_key=True, serialize=False)),
                ('wu', models.CharField(db_column='WU', max_length=4, unique=True)),
                ('div', models.CharField(db_column='DIV', max_length=255)),
                ('wu_desc', models.CharField(db_column='Work Unit Description', max_length=255)),
                ('div_group', models.CharField(db_column='Division Group', max_length=255)),
                ('subdiv', models.CharField(db_column='SubDivision', max_length=255)),
            ],
            options={
                'db_table': 'tblWorkUnitDivisionJoeSubs',
                'managed': False,
            },
        ),
    ]
