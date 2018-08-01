# Generated by Django 2.0.7 on 2018-08-01 05:34

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('rsvp_bot', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Channel',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('discord_id', models.CharField(max_length=128)),
                ('name', models.CharField(max_length=256)),
            ],
        ),
        migrations.RemoveField(
            model_name='eventboard',
            name='channel_name',
        ),
        migrations.AddField(
            model_name='server',
            name='discord_id',
            field=models.CharField(default=0, max_length=128),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='eventboard',
            name='channel',
            field=models.ForeignKey(default=0, on_delete=django.db.models.deletion.CASCADE, to='rsvp_bot.Channel'),
            preserve_default=False,
        ),
    ]
