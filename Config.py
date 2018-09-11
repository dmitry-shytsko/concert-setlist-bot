import json
import os


class Config:
    def __init__(self):
        configFile = open("conf.json", "r")
        configJson = json.loads(configFile.read())
        configFile.close()

        self.devMode = int(configJson["devMode"])

        configDict = configJson["devConfig"] if self.devMode > 0 else configJson["prodConfig"]

        self.setlistFmKey = None
        self.telegramKey = None
        self.botOwner = None

        if "botOwner" in configJson:
            self.botOwner = configJson["botOwner"]

        if "setlistFmKey" in configDict:
            self.setlistFmKey = configDict["setlistFmKey"]

        if "telegramKey" in configDict:
            self.telegramKey = configDict["telegramKey"]

        if self.setlistFmKey is None:
            self.setlistFmKey = os.getenv("SETLISTFM_KEY")

        if self.telegramKey is None:
            self.telegramKey = os.getenv("TELEGRAM_KEY")

        if self.botOwner is None:
            self.botOwner = os.getenv("BOT_OWNER")

    def checkBotOwner(self, user):
        if self.botOwner is None:
            return False

        if user is None:
            return False

        if user.username is None:
            return False

        return user.username == self.botOwner

    def checkKeys(self):
        if self.setlistFmKey is None:
            return False

        if self.telegramKey is None:
            return False

        return True
