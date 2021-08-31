from datetime import datetime, timedelta


class State:
    started: datetime
    ended: datetime
    name: str
    is_started = True

    def __init__(self, name):
        self.name = name

    def start(self):
        self.started = datetime.now()

    def end(self):
        self.ended = datetime.now()

    def get_period(self):
        try:
            return self.chop_microseconds(self.ended - self.started)
        except AttributeError:
            return self.chop_microseconds(datetime.now() - self.started)

    def __repr__(self):
        return str(self.get_period())

    @staticmethod
    def chop_microseconds(delta):
        return delta - timedelta(microseconds=delta.microseconds)
