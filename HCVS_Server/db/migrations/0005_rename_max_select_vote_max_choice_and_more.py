# Generated by Django 4.1.6 on 2023-06-19 03:11

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('db', '0004_rename_choice_vote_choice'),
    ]

    operations = [
        migrations.RenameField(
            model_name='vote',
            old_name='max_select',
            new_name='max_choice',
        ),
        migrations.RenameField(
            model_name='vote',
            old_name='min_select',
            new_name='min_choice',
        ),
    ]
