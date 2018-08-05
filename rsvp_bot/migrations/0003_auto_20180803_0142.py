# Generated by Django 2.0.7 on 2018-08-03 01:42

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('rsvp_bot', '0002_auto_20180801_0534'),
    ]

    operations = [
        migrations.CreateModel(
            name='Message',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('discord_id', models.CharField(max_length=128)),
                ('timestamp', models.DateTimeField()),
                ('content', models.CharField(max_length=2048)),
            ],
        ),
        migrations.AlterField(
            model_name='event',
            name='message',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='rsvp_bot.Message'),
        ),
        migrations.AddField(
            model_name='eventboard',
            name='message',
            field=models.ForeignKey(default=0, on_delete=django.db.models.deletion.CASCADE, to='rsvp_bot.Message'),
            preserve_default=False,
        ),
    ]
