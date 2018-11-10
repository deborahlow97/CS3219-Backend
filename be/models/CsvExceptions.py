
class TimeDataError(Exception):
    def __init__(self, msg):
        self.message = msg

class DateDataError(Exception):
    def __init__(self, msg):
        self.message = msg

class DateAndTimeDataError(Exception):
    def __init__(self, msg):
        self.message = msg

