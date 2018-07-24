
from collections import defaultdict
from discord.utils import find
import arrow

NUMBER_EMOJIS = ['1⃣', '2⃣', '3⃣', '4⃣', '5⃣', '6⃣', '7⃣', '8⃣', '9⃣', '🔟']
QUESTION_EMOJIS = ['❓', '❔']
RECOGNIZED_EMOJIS = NUMBER_EMOJIS + QUESTION_EMOJIS
EMOJI_TEXT = {'1⃣': '1', '2⃣': '2', '3⃣': '3', '4⃣': '4', '5⃣': '5',
              '6⃣': '6', '7⃣': '7', '8⃣': '8', '9⃣': '9', '🔟': '10', '❓': '?', '❔': '?'}


def parse_expiration(time_text):
    if time_text.lower() == 'never':
        return float('Inf')

    time_in_seconds = 0
    split_time = time_text.split()
    time_iter = iter(split_time)
    for time in time_iter:
        amount = float(time)
        time_unit = next(time_iter).lower()
        if time_unit in ['sec', 'secs', 'second', 'seconds']:
            time_in_seconds += amount
        elif time_unit in ['minutes', 'minute', 'mins', 'min']:
            time_in_seconds += amount * 60
        elif time_unit in ['hours', 'hour']:
            time_in_seconds += amount * 60 * 60
        elif time_unit in ['days', 'day']:
            time_in_seconds += amount * 60 * 60 * 24
    return time_in_seconds


class RSVPMessage():
    def __init__(self, message, expiration=60 * 60 + 60 * 45):
        self.message = message
        self.content = message.content
        self.alerts = []
        # expiration is time in seconds until alerts become untracked.
        self.expiration = expiration

    def get_alert(self, message):
        for alert in self.alerts:
            if alert.message.id == message.id:
                return alert
        return None

    def delete_alert(self, message):
        self.alerts = [
            alert for alert in self.alerts if alert.message.id != message.id]

    def create_alert(self, message):
        alert = self.get_alert(message)
        if (not alert and message.id != self.message.id and
                (arrow.utcnow() - arrow.get(message.timestamp)).seconds < self.expiration):
            alert = Alert(message, self.expiration)
            self.alerts = [alert] + self.alerts
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
            content = '*No RSVPs*'
        self.content = content

    def set_expiration(self, expiration):
        self.expiration = expiration
        for alert in self.alerts:
            alert.set_expiration(expiration)


class Alert():
    def __init__(self, message, expiration=None):
        self.responses = Responses()
        self.message = message
        self.composed_content = message.content
        self.post_date = message.timestamp
        self.expiration = expiration

    @property
    def is_expired(self):
        return (arrow.utcnow() - arrow.get(self.post_date)).seconds > self.expiration

    def set_expiration(self, expiration):
        self.expiration = expiration

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
        if rsvps:
            content += f'\nRSVPs ({total_rsvps}): {rsvps}'
        if maybes:
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
