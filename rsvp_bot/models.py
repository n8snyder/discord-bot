from django.db import models


class User(models.Model):
    name = models.CharField(max_length=256)
    discord_id = models.CharField(max_length=128)
    nickname = models.CharField(max_length=256)


class Attendee(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    emoji = models.CharField(max_length=1)


class Event(models.Model):
    message = models.CharField(max_length=2048)
    attendees = models.ManyToManyField(Attendee)


class Server(models.Model):
    name = models.CharField(max_length=256)
    users = models.ManyToManyField(User)


class EventBoard(models.Model):
    server = models.ForeignKey(Server, on_delete=models.CASCADE)
    channel_name = models.CharField(max_length=256)
    # expirations is time in seconds before event expires
    expiration = models.IntegerField()
    events = models.ManyToManyField(Event)
