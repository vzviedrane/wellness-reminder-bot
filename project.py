import os
import json
import telebot
import requests
from typing import Dict, Optional, Union
from dotenv import load_dotenv
from threading import Thread, Event
from telebot.types import ReplyKeyboardMarkup
import time

# Declare global variables
TOKEN = ""
bot = None
DEFAULT_INTERVALS: Dict[str, int] = {}

def main():
    # Load configuration
    global DEFAULT_INTERVALS
    DEFAULT_INTERVALS = load_config()

    # Initialize the bot and its handlers
    initialize_bot()

    # Run the bot
    run_bot(bot)

def load_config() -> Dict[str, int]:
    """
    Loads the bot token from environment variables and configuration settings from a JSON file.

    Returns:
        Dict[str, int]: A dictionary containing default intervals for reminders.
    """
    global TOKEN, bot

    # Load the bot token from environment variables
    load_dotenv()
    TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
    if not TOKEN:
        raise ValueError("TELEGRAM_BOT_TOKEN is not set in the .env file.")

    # Initialize the bot with the loaded token
    bot = telebot.TeleBot(TOKEN)

    # Load intervals from the JSON configuration file
    with open("config.json", "r") as config_file:
        config: Dict[str, Dict[str, int]] = json.load(config_file)
    return config["intervals"]


# Function 2: Initialize bot commands and set up the Chatbot class
def initialize_bot() -> None:
    """
    Sets up bot command handlers and initializes the Chatbot class.
    """
    global chatbot
    chatbot = Chatbot(bot)

    @bot.message_handler(commands=['start'])
    def handle_start(message: telebot.types.Message) -> None:
        user_id: str = str(message.chat.id)
        chatbot.start(user_id)

    @bot.message_handler(func=lambda message: True)
    def handle_message(message: telebot.types.Message) -> None:
        user_id: str = str(message.chat.id)
        chatbot.handle_user_input(user_id, message.text)

# Function 3: Start the bot with polling and error handling
def run_bot(bot: telebot.TeleBot) -> None:
    """
    Starts the bot's polling loop. Handles Ctrl+C for stopping.
    """
    try:
        print("Bot is running. Press Ctrl+C to stop.")
        bot.polling(non_stop=True)
    except KeyboardInterrupt:
        print("\nBot stopped by user.")
    finally:
        # Stop polling explicitly (if necessary)
        if hasattr(bot, 'stop_polling'):
            bot.stop_polling()
        print("Bot has exited.")


# Classes for reminders and bot functionality
class User:
    """
    Represents a bot user.

    Attributes:
        user_id (str): The unique ID of the user.
        name (str): The name of the user, defaulting to "User <user_id>" if not provided.
    """

    def __init__(self, user_id: str, name: Optional[str] = None):
        self.user_id: str = user_id
        self.name: str = name or f"User {user_id}"

class Reminder:
    """
    Base class for creating reminders.

    Attributes:
        user_id (str): The ID of the user receiving the reminder.
        interval (int): The time interval in minutes for the reminder.
    """

    def __init__(self, user_id: str, interval: int):
        self.user_id: str = user_id
        self.interval: int = interval
        self.stop_event: Event = Event()  # Event to manage stopping the thread

    def start(self) -> None:
        """
        Starts the reminder thread, sending reminders at the specified interval.
        """
        # Repeatedly send reminders at a set interval
        def run() -> None:
            while not self.stop_event.is_set():
                self.send_reminder()
                self.stop_event.wait(self.interval * 60)

        # Stop any existing thread before starting a new one
        self.stop_existing_thread()

        # Start a new thread for the reminder
        reminder_thread: Thread = Thread(target=run, daemon=True)
        if self.user_id not in active_reminders:
            active_reminders[self.user_id] = {}
        active_reminders[self.user_id][type(self).__name__] = (reminder_thread, self.stop_event)
        reminder_thread.start()

    def stop_existing_thread(self) -> None:
        """
        Stops any existing reminder thread for this reminder type.
        """
        if self.user_id in active_reminders and type(self).__name__ in active_reminders[self.user_id]:
            _, stop_event = active_reminders[self.user_id][type(self).__name__]
            stop_event.set()
            del active_reminders[self.user_id][type(self).__name__]

    def send_reminder(self) -> None:
        """
        Sends a reminder message to the user. To be implemented by subclasses.
        """
        raise NotImplementedError

    def send_message_with_timeout(self, message: str, retries: int = 3) -> None:
        """
        Sends a message with a retry mechanism in case of a timeout.
        """
        for attempt in range(retries):
            try:
                bot.send_message(self.user_id, message)
                print(f"Message sent to user {self.user_id} successfully.")
                return
            except requests.exceptions.ReadTimeout:
                print(f"Timeout sending message to user {self.user_id}. Retrying ({attempt + 1}/{retries})...")
                time.sleep(2)
            except Exception as e:
                print(f"An error occurred: {e}")
                break
        print(f"Failed to send message to user {self.user_id} after {retries} attempts.")

class HydrationReminder(Reminder):
    """
    Reminder to drink water, inherits from Reminder.
    """
    def send_reminder(self) -> None:
        message: str = "💧 Time to drink water!"
        self.send_message_with_timeout(message)

class StretchReminder(Reminder):
    """
    Reminder to stretch, inherits from Reminder.
    """
    def send_reminder(self) -> None:
        message: str = "🧘 Time to stretch!"
        self.send_message_with_timeout(message)

class BreakReminder(Reminder):
    """
    Reminder to take a break, inherits from Reminder.
    """
    def send_reminder(self) -> None:
        message: str = "⏰ Take a break!"
        self.send_message_with_timeout(message)

class Chatbot:
    """
    Manages bot commands and user interactions.
    """

    def __init__(self, bot_instance: telebot.TeleBot):
        self.bot: telebot.TeleBot = bot_instance

    def start(self, user_id: str) -> None:
        """
        Initiates the bot by displaying the main menu to the user.
        """
        user: User = User(user_id)
        self.show_main_menu(user)

    def show_main_menu(self, user: User) -> None:
        """
        Displays the main menu with options for setting and stopping reminders.
        """
        markup: ReplyKeyboardMarkup = self.build_main_menu(user)
        self.bot.send_message(user.user_id, "Choose an option below:", reply_markup=markup)

    def build_main_menu(self, user: User) -> ReplyKeyboardMarkup:
        """
        Builds the main menu markup with available options.
        """
        markup: ReplyKeyboardMarkup = ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add("Set Water Reminder", "Set Stretch Reminder", "Set Break Reminder")
        markup.add("Show Preferences")
        if user.user_id in active_reminders:
            if "HydrationReminder" in active_reminders[user.user_id]:
                markup.add("Stop Water Reminder")
            if "StretchReminder" in active_reminders[user.user_id]:
                markup.add("Stop Stretch Reminder")
            if "BreakReminder" in active_reminders[user.user_id]:
                markup.add("Stop Break Reminder")
        return markup

    def handle_user_input(self, user_id: str, input_str: str) -> None:
        """
        Processes user input to set or stop reminders based on the command received.
        """
        user: User = User(user_id)
        input_str = input_str.lower()
        if input_str == "set water reminder":
            self.set_reminder(user_id, "water", "HydrationReminder", user)
        elif input_str == "set stretch reminder":
            self.set_reminder(user_id, "stretch", "StretchReminder", user)
        elif input_str == "set break reminder":
            self.set_reminder(user_id, "break", "BreakReminder", user)
        elif input_str == "show preferences":
            prefs_text: str = "\n".join([f"{key.capitalize()} reminder: every {value} minutes" for key, value in DEFAULT_INTERVALS.items()])
            self.bot.send_message(user_id, f"Default reminder settings:\n{prefs_text}")
        elif input_str == "stop water reminder":
            self.stop_reminder(user_id, "HydrationReminder", "Water reminder stopped.")
        elif input_str == "stop stretch reminder":
            self.stop_reminder(user_id, "StretchReminder", "Stretch reminder stopped.")
        elif input_str == "stop break reminder":
            self.stop_reminder(user_id, "BreakReminder", "Break reminder stopped.")

    def set_reminder(self, user_id: str, reminder_type: str, reminder_class: str, user: User) -> None:
        """
        Sets a specific type of reminder and updates the main menu.
        """
        self.stop_reminder(user_id, reminder_class, "")
        interval: int = DEFAULT_INTERVALS.get(reminder_type, 1)
        reminder: Reminder = globals()[reminder_class](user_id, interval)
        reminder.start()
        message_text: str = f"{reminder_type.capitalize()} reminder set for every {interval} minutes.\n\n"
        message_text += "Use the menu below to stop the reminder if needed."
        self.bot.send_message(user_id, message_text, reply_markup=self.build_main_menu(user))

    def stop_reminder(self, user_id: str, reminder_type: str, stop_message: str) -> None:
        """
        Stops a specific reminder and updates the menu.
        """
        if user_id in active_reminders and reminder_type in active_reminders[user_id]:
            _, stop_event = active_reminders[user_id].pop(reminder_type)
            stop_event.set()
            if not active_reminders[user_id]:
                del active_reminders[user_id]
            if stop_message:
                self.bot.send_message(user_id, stop_message)
        self.bot.send_message(user_id, "Choose an option below:", reply_markup=self.build_main_menu(User(user_id)))

# Active reminders dictionary to manage user reminders
active_reminders: Dict[str, Dict[str, Union[Thread, Event]]] = {}

# Main Script Execution
if __name__ == "__main__":
    main()
