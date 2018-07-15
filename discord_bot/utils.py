
from collections import defaultdict
from discord.utils import find

RECOGNIZED_EMOJIS = ['1⃣', '2⃣', '3⃣', '4⃣',
                     '5⃣', '6⃣', '7⃣', '8⃣', '9⃣', '🔟', '❓', '❔']
EMOJI_TEXT = {'1⃣': '1', '2⃣': '2', '3⃣': '3', '4⃣': '4', '5⃣': '5',
              '6⃣': '6', '7⃣': '7', '8⃣': '8', '9⃣': '9', '🔟': '10', '❓': '?', '❔': '?'}


class ReservedMessage():
    def __init__(self, message):
        self.message = message
        self.content = message.content
        self.alerts = []

    def get_alert(self, content):
        for alert in self.alerts:
            if alert.original_content == content:
                return alert
        return None

    def get_or_create_alert(self, content):
        alert = self.get_alert(content)
        if not alert:
            alert = Alert(content)
            self.alerts.append(alert)
        return alert

    def update_alerts(self):
        updated_alerts = []
        for alert in self.alerts:
            if any(alert.responses.values()):
                updated_alerts.append(alert)
        self.alerts = updated_alerts

    def compose_content(self):
        content = ''
        for alert in self.alerts:
            alert.compose_content()
            content += f'\n{alert.content}'
        if not content:
            content = '*Reserved*'
        self.content = content


class Alert():
    def __init__(self, content):
        self.responses = Responses()
        self.original_content = content
        self.content = content

    def edit_content(self, content):
        self.content = content

    def edit_original_content(self, content):
        self.original_content = content

    def compose_content(self):
        content = self.original_content
        content += '\nRSVPs:'
        for emoji, users in self.responses.items():
            for user in users:
                content += f' {user.name} ({EMOJI_TEXT[emoji]})'
        self.content = content


class Responses(defaultdict):
    def __init__(self):
        defaultdict.__init__(self, list)

    def post(self, reaction, user):
        self[reaction.emoji].append(user)

    def delete(self, reaction, user):
        self[reaction.emoji] = [
            responded_user for responded_user in self[reaction.emoji] if responded_user != user]


def is_alert_channel(channel):
    return 'alert' in channel.name.lower()


def get_original_content(content):
    return content.split('RSVPs:')[0]


def get_channel_message(client, channel, content):
    #  returns the first message with the given content in the given channel.
    original_content = get_original_content(content)
    existing_message = find(lambda m: get_original_content(
        m.content) == original_content and m.channel == channel, client.messages)
    return existing_message


def add_user_to_content(message, reaction, user):
    # adds names to message content
    print(message.content)
    message_content = message.content.split('RSVPs:')[0]
    try:
        current_rsvps = message.content.split('RSVPs:')[1]
    except IndexError:
        updated_rsvps = f"{user.name} {reaction.emoji}"
    else:
        updated_rsvps = f"{current_rsvps}, {user.name} {reaction.emoji}"
    return f'{message_content} RSVPs: {updated_rsvps}'


def remove_user_from_content(message, reaction, user):
    # remove user from message
    return message.content
