from datetime import datetime, timedelta


class State:
    started: datetime
    ended: datetime
    name: str
    period: (timedelta, None)

    def __init__(self, name):
        self.name = name

    def start(self):
        self.started = datetime.now()

    def end(self):
        self.ended = datetime.now()
        self.period = None

    def get_period(self):
        try:
            if self.period and self.ended:
                return self.period
            self.period = self.chop_microseconds(self.ended - self.started)
        except AttributeError:
            self.period = self.chop_microseconds(datetime.now() - self.started)
        finally:
            return self.period

    def __repr__(self):
        return str(self.get_period())

    def __add__(self, other):
        s = State(self.name)
        s.period = self.get_period() + other.get_period()
        s.started = datetime.now()
        s.ended = datetime.now()
        return s

    @staticmethod
    def chop_microseconds(delta):
        return delta - timedelta(microseconds=delta.microseconds)
