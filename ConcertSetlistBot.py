import Config
import Setlist
import logging

from telegram.ext import Updater, CommandHandler, MessageHandler, Filters


config = Config.Config()

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)


# noinspection PyUnusedLocal
def startCommandHandler(bot, update):
    startMessage = "Bot Started. Please send in the name of the artist or use the /help command"
    update.message.reply_text(startMessage)


def helpCommandHandler(bot, update):
    helpFile = open("help.html", "r")
    bot.send_message(update.message.chat_id, helpFile.read(), "HTML")
    helpFile.close()


def whatsNewCommandHandler(bot, update):
    whatsNewFile = open("whatsnew.html", "r")
    bot.send_message(update.message.chat_id, whatsNewFile.read(), "HTML")
    whatsNewFile.close()


def artistNameHandler(bot, update):
    if update.message.text is not None and len(update.message.text) > 0:
        setlistParams = Setlist.SetlistParams(update.message.text)
        artistSetlists = Setlist.Setlists(setlistParams.artist, config)

        if update.message.from_user is not None:
            logger.info('Setlist for "%s" requested by "%s"', setlistParams.artist, update.message.from_user)
        else:
            logger.info('Setlist for "%s" requested by unknown user', setlistParams.artist)

        if artistSetlists.code == 0:
            setlistsToDisplay = artistSetlists.getMostRecentSetlists(setlistParams.count)

            if len(setlistsToDisplay) > 0:
                setlistsToDisplayIterator = iter(setlistsToDisplay)
                for setlistToDisplay in setlistsToDisplayIterator:
                    bot.send_message(update.message.chat_id, setlistToDisplay.setlistAsHtml(), "HTML")
            else:
                update.message.reply_text("None Found")
        else:
            update.message.reply_text(artistSetlists.status)
    else:
        update.message.reply_text("Nothing to look for")


# noinspection PyUnusedLocal
def errorHandler(bot, update, error):
    logger.warning('Update "%s" caused error "%s"', update, error)


def main():
    updater = Updater(config.telegramKey)

    if config.checkKeys():
        logger.info("API keys loaded OK, we're all set.")
    else:
        logger.error("API keys not loaded. Terminating the bot.")
        return

    updater.dispatcher.add_handler(CommandHandler("start", startCommandHandler))
    updater.dispatcher.add_handler(CommandHandler("help", helpCommandHandler))
    updater.dispatcher.add_handler(CommandHandler("whatsnew", whatsNewCommandHandler))
    updater.dispatcher.add_handler(MessageHandler(Filters.text, artistNameHandler))
    updater.dispatcher.add_error_handler(errorHandler)

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
