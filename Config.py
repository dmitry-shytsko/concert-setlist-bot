import json

class Config:
    def __init__(self):
        configFile = open("config.json", "r")
        configJson = json.loads(configFile.read())
        configFile.close()

        devMode = int(configJson["devMode"])

        configDict = configJson["devConfig"] if devMode > 0 else configJson["prodConfig"]

        self.setlistFmKey = configDict["setlistFmKey"]
        self.telegramKey = configDict["telegramKey"]
