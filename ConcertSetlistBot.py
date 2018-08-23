import json
import requests

setlistFmUrl = 'https://api.setlist.fm/rest/1.0/search/setlists'
setlistFmHeaders = {'x-api-key': 'f0d0f1f7-ddab-4562-a334-8ad7b76c2c7e', 'Accept': 'application/json'}

telegramKey = "658104325:AAHe1V-0c2Tt0cjo1gKvJqHl15ppVmdng8M"


class SetlistSong:

    def __init__(self, data, encore):
        self.name = data['name']
        self.encore = encore

        if 'tape' in data:
            self.tape = data['tape']
        else:
            self.tape = False

        if self.tape and len(self.name) == 0:
            self.name = "Intro"

        if 'cover' in data:
            self.originalArtist = data['cover']['name']
        else:
            self.originalArtist = None

    def displayName(self):
        displayName = self.name

        if self.tape:
            displayName += " (Tape)"

        if self.encore:
            displayName += " (Encore)"

        if self.originalArtist is not None:
            displayName += " (" + self.originalArtist + " song)"

        return displayName

    def displayNameHtml(self, index):
        prefix = "📼" if self.tape else str(index) + "."
        postfix = ""

        if self.originalArtist is not None:
            originalArtistTemplate = "<i>({} song)</i>"
            postfix = originalArtistTemplate.format(self.originalArtist)

        displayNameTemplate = "{}\t{} {}"

        return displayNameTemplate.format(prefix, self.name, postfix).strip()


class Setlist:

    def __init__(self, data, exactArtistName):
        self.eventDate = data['eventDate']
        self.artist = data['artist']['name']
        self.venue = data['venue']['name']
        self.city = data['venue']['city']['name']
        self.country = data['venue']['city']['country']['name']
        self.url = data['url']

        if self.artist.lower() != exactArtistName.lower():
            self.inexactArtistName = True
        else:
            self.inexactArtistName = False

        if 'info' in data:
            self.info = data['info']
        else:
            self.info = None

        if 'tour' in data:
            self.tour = data['tour']['name']
        else:
            self.tour = None

        self.songs = []

        setsArrayIterator = iter(data['sets']['set'])

        for setsArray in setsArrayIterator:
            encore = False
            if 'encore' in setsArray and setsArray['encore'] > 0:
                encore = True

            songIterator = iter(setsArray['song'])
            for song in songIterator:
                self.songs.append(SetlistSong(song, encore))

    def getSongDisplayNames(self):
        songDisplayNames = []

        for song in iter(self.songs):
            songDisplayNames.append(song.displayName())

        return songDisplayNames

    def displaySetlist(self):
        print("Event Date : ", self.eventDate)
        print("Artist : ", self.artist)
        print("Venue : ", self.venue)
        print("City : ", self.city)
        print("Country : ", self.country)
        print("Songs : ", self.getSongDisplayNames())
        print("URL : ", self.url)

        if self.tour is not None:
            print("Tour : ", self.tour)

        if self.info is not None:
            print("Info : ", self.info)

        print("----------")

    def setlistAsHtml(self):
        songsHtml = ""
        songIndex = 1
        encoreDelimiter = False

        for song in iter(self.songs):
            if len(songsHtml) > 0:
                songsHtml += '\n'

            if song.encore and encoreDelimiter is False:
                songsHtml += "\n<i>Encore</i>\n\n"
                encoreDelimiter = True

            songsHtml += song.displayNameHtml(songIndex)

            if song.tape is False:
                songIndex += 1

        htmlTemplate = "<b>Artist: </b>{}\n<b>Date: </b>{}\n<b>Venue: </b>{}, {}, {}\n\n{}\n\n" \
            "Visit the <a href=\"{}/\">setlist.fm page</a> for this show"

        return htmlTemplate.format(self.artist, self.eventDate, self.venue, self.city, self.country, songsHtml, self.url)

    def isEmpty(self):
        return len(self.songs) == 0


class Setlists:

    def __init__(self, artistName):
        self.code = 0
        self.artistName = artistName

        apiParams = {'artistName': artistName}
        apiResponse = requests.get(url=setlistFmUrl, params=apiParams, headers=setlistFmHeaders)
        apiJson = json.loads(apiResponse.text)

        if 'code' in apiJson:
            self.code = apiJson['code']
            if 'status' in apiJson:
                self.status = apiJson['status']
            if 'message' in apiJson:
                self.message = apiJson['message']
            return

        self.setlists = []

        for setlistJson in iter(apiJson["setlist"]):
            setlist = Setlist(setlistJson, self.artistName)

            if setlist.isEmpty() is False:
                if setlist.inexactArtistName is False:
                    self.setlists.append(setlist)

    def displaySetlists(self):
        for setlist in iter(self.setlists):
            setlist.displaySetlist()

    def getMostRecentSetlist(self):
        if len(self.setlists) > 0:
            return self.setlists[0]

    def getMostRecentSetlists(self, count):
        realCount = min(len(self.setlists), count)

        setlists = []

        for index in range(0, realCount):
            setlists.append(self.setlists[index])

        return setlists


class TelegramHandler:

    def __init__(self, token):
        self.token = token
        self.api_url = "https://api.telegram.org/bot{}/".format(token)

    def get_updates(self, offset=None, timeout=15):
        method = 'getUpdates'
        params = {'timeout': timeout, 'offset': offset}
        resp = requests.get(self.api_url + method, params)
        result_json = resp.json()['result']
        return result_json

    def send_message(self, chat_id, text):
        params = {'chat_id': chat_id, 'text': text, 'parse_mode': 'HTML'}
        method = 'sendMessage'
        resp = requests.post(self.api_url + method, params)
        return resp

    def get_last_update(self):
        get_result = self.get_updates()

        if len(get_result) > 0:
            last_update = get_result[-1]
        else:
            last_update = None

        return last_update


def testSetlistFm(artistName):
    artistSetlists = Setlists(artistName)

    if artistSetlists.code == 0:
        artistSetlist = artistSetlists.getMostRecentSetlist()

        if artistSetlist is None:
            print("None Found")
        else:
            artistSetlist.displaySetlist()
    else:
        print(artistSetlists.status)

# Uncomment this to test the setlist.fm integration
# Iron Maiden is a good example of the band with a complex setlist (intros, covers, encores)
# testSetlistFm("Iron Maiden")


def main():
    botHandler = TelegramHandler(telegramKey)

    # Ignoring all pending updates before the start of the bot
    lastUpdate = botHandler.get_last_update()
    new_offset = None

    if lastUpdate is not None:
        lastUpdateId = lastUpdate['update_id']
        new_offset = lastUpdateId + 1

    while True:
        updates = botHandler.get_updates(new_offset)

        updatesIterator = iter(updates)
        for update in updatesIterator:
            chatId = update['message']['chat']['id']
            message = update['message']['text'].strip()
            lastUpdateId = update['update_id']
            new_offset = lastUpdateId + 1

            if message is None or len(message) == 0:
                continue

            if message[0] == '/':
                if message.lower() == '/start':
                    botHandler.send_message(chatId, "Bot Started. Please send in the name of the artist or use "\
                                                    "the /help command")
                elif message.lower() == '/help':
                    helpFile = open("help.html", "r")
                    botHandler.send_message(chatId, helpFile.read())
                elif message.lower() == '/whatsnew':
                    helpFile = open("whatsnew.html", "r")
                    botHandler.send_message(chatId, helpFile.read())
                else:
                    botHandler.send_message(chatId, "Sorry, this is an unknown command...")
            else:
                print(message)

                artistName = message
                setlistCount = 1
                params = message.split(' +')

                if len(params) == 2:
                    # noinspection PyBroadException
                    try:
                        setlistCount = int(params[1]) + 1
                        artistName = params[0]
                    except:
                        pass

                artistSetlists = Setlists(artistName)

                if artistSetlists.code == 0:
                    setlistsToDisplay = artistSetlists.getMostRecentSetlists(setlistCount)

                    if len(setlistsToDisplay) > 0:
                        setlistsToDisplayIterator = iter(setlistsToDisplay)
                        for setlistToDisplay in setlistsToDisplayIterator:
                            botHandler.send_message(chatId, setlistToDisplay.setlistAsHtml())
                    else:
                        botHandler.send_message(chatId, "None Found")
                else:
                    botHandler.send_message(chatId, artistSetlists.status)


if __name__ == '__main__':
    main()
