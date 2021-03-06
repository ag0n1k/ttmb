"""
Simple Bot to send timed Telegram messages.
This Bot uses the Updater class to handle the bot and the JobQueue to send
timed messages.
First, a few handler functions are defined. Then, those functions are passed to
the Dispatcher and registered at their respective places.
Then, the bot is started and runs until we press Ctrl-C on the command line.
Usage:
Basic Alarm Bot example, sends a message after a set time.
Press Ctrl-C on the command line or send a signal to the process to stop the
bot.
"""

import logging
import os

from datetime import datetime
from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext, MessageHandler, Filters

from state import State

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

logger = logging.getLogger(__name__)

global_start = datetime.now()
global_period = 25*60

# Define a few command handlers. These usually take the two arguments update and
# context. Error handlers also receive the raised TelegramError object in error.
# Best practice would be to replace context with an underscore,
# since context is an unused local variable.
# This being an example and not having context present confusing beginners,
# we decided to have it present as context.
def start(update: Update, context: CallbackContext) -> None:
    """Sends explanation on how to use the bot."""
    update.message.reply_text('Hi! Use /run to start a timer')


def run(update: Update, context: CallbackContext) -> None:
    """Sends explanation on how to use the bot."""
    global global_start
    if context.user_data.get('category', None):
        stat(update, context)
    context.user_data['category'] = []
    context.user_data['current'] = State('start')
    context.user_data['category'].append(context.user_data['current'])
    context.user_data['current'].start()
    update.message.reply_text(f'Started start at {context.user_data["current"].started}')
    global_start = datetime.now()
    remove_job_if_exists(str(update.message.chat_id), context)


def stat(update: Update, context: CallbackContext) -> None:
    """Sends explanation on how to use the bot."""
    res = {}
    for i in context.user_data["category"]:
        item = res.get(i.name, None)
        if not item:
            res.update({i.name: i})
        else:
            res.update({i.name: i+item})

    update.message.reply_text('Started at {global_start}\nSpent {spent}\nPeriod {period} min\n\n'
                              'Stat:\n{res:>20}'.format(global_start=global_start, spent=datetime.now() - global_start,
                                                        period=global_period / 60,
                                                        res="\n".join([f"{k} : {v}" for k, v in res.items()])))


def change(update: Update, context: CallbackContext) -> None:
    context.user_data['current'].end()
    state = State(update.message.text.lower())
    state.start()
    update.message.reply_text(
        f'Spent on {context.user_data["current"].name} {context.user_data["current"].get_period()}')
    context.user_data['current'] = state
    context.user_data['category'].append(state)

    remove_job_if_exists(str(update.message.chat_id), context)
    context.job_queue.run_repeating(callback=alarm, interval=global_period, context=update.message.chat_id,
                                    name=str(update.message.chat_id))


def alarm(context: CallbackContext) -> None:
    """Send the alarm message."""
    job = context.job
    context.bot.send_message(job.context, text='You have to break! 5 minutes')


def remove_job_if_exists(name: str, context: CallbackContext) -> bool:
    """Remove job with given name. Returns whether job was removed."""
    current_jobs = context.job_queue.get_jobs_by_name(name)
    if not current_jobs:
        return False
    for job in current_jobs:
        job.schedule_removal()
    return True


def set_timer(update: Update, context: CallbackContext) -> None:
    """Add a job to the queue."""
    global global_period
    try:
        # args[0] should contain the time for the timer in seconds
        due = int(context.args[0])
        if due < 0:
            update.message.reply_text('Sorry we can not go back to future!')
            return
        global_period = 60 * due
        update.message.reply_text(f'Timer successfully set to {global_period}')
    except (IndexError, ValueError):
        update.message.reply_text('Usage: /set <seconds>')


def unset(update: Update, context: CallbackContext) -> None:
    """Remove the job if the user changed their mind."""
    chat_id = update.message.chat_id
    job_removed = remove_job_if_exists(str(chat_id), context)
    text = 'Timer successfully cancelled!' if job_removed else 'You have no active timer.'
    update.message.reply_text(text)


def main() -> None:
    """Run bot."""
    # Create the Updater and pass it your bot's token.
    updater = Updater(os.getenv('TELEGRAM_TOKEN'), use_context=True)

    # Get the dispatcher to register handlers
    dispatcher = updater.dispatcher

    # on different commands - answer in Telegram
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("run", run))
    dispatcher.add_handler(CommandHandler("help", start))
    dispatcher.add_handler(CommandHandler("set", set_timer))
    dispatcher.add_handler(CommandHandler("stat", stat))
    dispatcher.add_handler(MessageHandler(Filters.all, change))
    # Start the Bot
    updater.start_polling()

    # Block until you press Ctrl-C or the process receives SIGINT, SIGTERM or
    # SIGABRT. This should be used most of the time, since start_polling() is
    # non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()
