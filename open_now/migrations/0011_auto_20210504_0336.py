# Generated by Django 3.2 on 2021-05-04 03:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('open_now', '0010_discussion_email'),
    ]

    operations = [
        migrations.AlterField(
            model_name='discussion',
            name='email',
            field=models.CharField(default='Guest', max_length=200),
        ),
        migrations.AlterField(
            model_name='forum',
            name='email',
            field=models.CharField(default='Guest', max_length=200, null=True),
        ),
    ]
