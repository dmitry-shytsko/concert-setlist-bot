import Config
import Setlist
import Telegram


def testSetlistFm(artistName, config):
    artistSetlists = Setlist.Setlists(artistName, config)

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
    config = Config.Config()

    if config.checkKeys():
        print("API keys loaded OK, we're all set.")
    else:
        print("API keys not loaded. Terminating the bot.")
        return

    botHandler = Telegram.TelegramHandler(config.telegramKey)

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
                    helpFile.close()
                elif message.lower() == '/whatsnew':
                    helpFile = open("whatsnew.html", "r")
                    botHandler.send_message(chatId, helpFile.read())
                    helpFile.close()
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

                artistSetlists = Setlist.Setlists(artistName, config)

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
