# Generated by Django 4.1.6 on 2023-06-14 18:34

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='adminUser',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('username', models.CharField(max_length=20)),
                ('password', models.CharField(max_length=20)),
                ('name', models.CharField(max_length=20)),
                ('is_super', models.BooleanField(default=False)),
                ('can_GenNewCode', models.BooleanField(default=False)),
            ],
        ),
    ]
