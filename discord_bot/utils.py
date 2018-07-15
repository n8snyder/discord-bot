
from collections import defaultdict
from discord.utils import find

NUMBER_EMOJIS = ['1⃣', '2⃣', '3⃣', '4⃣', '5⃣', '6⃣', '7⃣', '8⃣', '9⃣', '🔟']
QUESTION_EMOJIS = ['❓', '❔']
RECOGNIZED_EMOJIS = NUMBER_EMOJIS + QUESTION_EMOJIS
EMOJI_TEXT = {'1⃣': '1', '2⃣': '2', '3⃣': '3', '4⃣': '4', '5⃣': '5',
              '6⃣': '6', '7⃣': '7', '8⃣': '8', '9⃣': '9', '🔟': '10', '❓': '?', '❔': '?'}


class ReservedMessage():
    def __init__(self, message):
        self.message = message
        self.content = message.content
        self.alerts = []

    def get_alert(self, message):
        for alert in self.alerts:
            if alert.message.id == message.id:
                return alert
        return None

    def get_or_create_alert(self, message):
        alert = self.get_alert(message)
        if not alert:
            alert = Alert(message)
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
            content += f'\n{alert.composed_content}\n'
        if not content:
            content = '*Reserved*'
        self.content = content


class Alert():
    def __init__(self, message):
        self.responses = Responses()
        self.message = message
        self.composed_content = message.content

    def update_message(self, message):
        self.message = message
        self.compose_content()

    def compose_content(self):
        content = self.message.content
        rsvps = ''
        total_rsvps = 0
        maybes = ''
        total_maybes = 0
        for emoji, users in self.responses.items():
            for user in users:
                if emoji in NUMBER_EMOJIS:
                    rsvps += f' {user.name} ({EMOJI_TEXT[emoji]})'
                    total_rsvps += int(EMOJI_TEXT[emoji])
                elif emoji in QUESTION_EMOJIS:
                    maybes += f' {user.name}'
                    total_maybes += 1
                else:
                    # This case is unhandled
                    pass

        content += f'\nRSVPs ({total_rsvps}): {rsvps}'
        content += f'\nMaybes ({total_maybes}): {maybes}'
        self.composed_content = content


class Responses(defaultdict):
    def __init__(self):
        defaultdict.__init__(self, list)

    def post(self, reaction, user):
        self[reaction.emoji].append(user)

    def delete(self, reaction, user):
        self[reaction.emoji] = [
            responded_user for responded_user in self[reaction.emoji] if responded_user != user]

    def member_responses(self, server):
        user_responses = defaultdict(list)
        for emoji, users in self.items():
            for user in users:
                user_responses[emoji].append(server.get_member(user.id))
        return user_responses


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
