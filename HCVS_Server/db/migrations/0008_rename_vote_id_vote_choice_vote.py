# Generated by Django 4.1.6 on 2023-06-19 03:18

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('db', '0007_vote_createuser_alter_vote_choice_vote_id'),
    ]

    operations = [
        migrations.RenameField(
            model_name='vote_choice',
            old_name='vote_id',
            new_name='vote',
        ),
    ]
