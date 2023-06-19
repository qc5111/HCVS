# Generated by Django 4.1.6 on 2023-06-18 23:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('db', '0002_alter_adminuser_password'),
    ]

    operations = [
        migrations.CreateModel(
            name='vote',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=20)),
                ('start_time', models.BigIntegerField()),
                ('end_time', models.BigIntegerField()),
                ('min_select', models.IntegerField()),
                ('max_select', models.IntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='choice',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('vote_id', models.IntegerField()),
                ('seq', models.IntegerField()),
                ('name', models.CharField(max_length=20)),
                ('description', models.CharField(max_length=100)),
            ],
            options={
                'unique_together': {('vote_id', 'seq')},
            },
        ),
    ]