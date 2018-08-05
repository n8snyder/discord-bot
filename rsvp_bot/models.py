from django.db import models


class User(models.Model):
    name = models.CharField(max_length=256)
    discord_id = models.CharField(max_length=128)
    nickname = models.CharField(max_length=256)


class Attendee(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    emoji = models.CharField(max_length=1)


class Message(models.Model):
    discord_id = models.CharField(max_length=128)
    timestamp = models.DateTimeField()
    content = models.CharField(max_length=2048)


class Event(models.Model):
    message = models.ForeignKey(Message, on_delete=models.CASCADE)
    attendees = models.ManyToManyField(Attendee)


class Server(models.Model):
    discord_id = models.CharField(max_length=128)
    name = models.CharField(max_length=256)
    users = models.ManyToManyField(User)


class Channel(models.Model):
    discord_id = models.CharField(max_length=128)
    name = models.CharField(max_length=256)


class EventBoard(models.Model):
    server = models.ForeignKey(Server, on_delete=models.CASCADE)
    channel = models.ForeignKey(Channel, on_delete=models.CASCADE)
    message = models.ForeignKey(Message, on_delete=models.CASCADE)
    # expirations is time in seconds before event expires
    expiration = models.IntegerField()
    events = models.ManyToManyField(Event)
