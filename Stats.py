import datetime


class Stats:
    def __init__(self):
        self.startTime = datetime.datetime.now()
        self.users = []
        self.requests = 0

    def recordStats(self, user):
        self.requests += 1

        if user is not None:
            if user.id not in self.users:
                self.users.append(user.id)

    def getStats(self):
        statsTemplate = "Processed {} requests from {} users since {}"
        return statsTemplate.format(self.requests, len(self.users), self.startTime).strip()
