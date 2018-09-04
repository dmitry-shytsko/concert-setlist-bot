import json
import requests


class SetlistParams:
    def __init__(self, params):
        self.artist = params
        self.count = 1
        paramsList = params.split(' +')

        if len(paramsList) == 2:
            # noinspection PyBroadException
            try:
                self.count = int(paramsList[1]) + 1
                self.artist = paramsList[0]
            except:
                pass


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
    def __init__(self, artistName, config):
        self.code = 0
        self.artistName = artistName

        setlistFmUrl = 'https://api.setlist.fm/rest/1.0/search/setlists'
        setlistFmHeaders = {'x-api-key': config.setlistFmKey, 'Accept': 'application/json'}

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
