# Generated by Django 4.1.6 on 2023-06-20 01:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('db', '0009_alter_vote_name_alter_vote_choice_name'),
    ]

    operations = [
        migrations.CreateModel(
            name='otpFailRecord',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('user_id', models.BigIntegerField()),
                ('ipAddress', models.CharField(max_length=15)),
                ('time', models.BigIntegerField()),
            ],
            options={
                'unique_together': {('user_id', 'time')},
            },
        ),
    ]