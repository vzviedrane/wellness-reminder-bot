# test_project.py

import sys
import os
import pytest
from unittest.mock import patch, MagicMock, mock_open
import telebot
from project import initialize_bot, Chatbot, User, load_config, run_bot

# Add the root directory to the Python path for proper imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Tests
def test_initialize_bot():
    mock_bot = MagicMock()
    with patch("project.Chatbot") as MockChatbot:
        with patch("project.bot", mock_bot):
            initialize_bot()
            MockChatbot.assert_called_once_with(mock_bot)
            assert mock_bot.message_handler.call_count == 2


def test_chatbot_reminder_integration():
    mock_bot = MagicMock()
    chatbot = Chatbot(mock_bot)
    user_id = "12345"
    user = User(user_id)
    mock_intervals = {"water": 30}
    with patch("project.DEFAULT_INTERVALS", mock_intervals):
        with patch("project.HydrationReminder") as MockReminder:
            mock_reminder_instance = MockReminder.return_value
            chatbot.set_reminder(user_id, "water", "HydrationReminder", user)
            mock_reminder_instance.start.assert_called_once()
            assert mock_bot.send_message.call_args.kwargs["reply_markup"].__class__ == telebot.types.ReplyKeyboardMarkup
            mock_bot.send_message.assert_called_with(
                user_id,
                "Water reminder set for every 30 minutes.\n\nUse the menu below to stop the reminder if needed.",
                reply_markup=mock_bot.send_message.call_args.kwargs["reply_markup"]
            )


def test_load_config():
    mock_env = patch("os.getenv", return_value="123456:ABC-DEF123456")
    mock_file = patch("builtins.open", mock_open(read_data='{"intervals": {"water": 30}}'))
    with mock_env, mock_file:
        result = load_config()
        assert result == {"water": 30}


def test_bot_performance_under_load():
    mock_bot = MagicMock()
    chatbot = Chatbot(mock_bot)
    num_users = 100
    mock_reminders = []
    mock_intervals = {"water": 30}
    with patch("project.DEFAULT_INTERVALS", mock_intervals):
        for i in range(1, num_users + 1):
            user_id = str(i)
            with patch("project.HydrationReminder") as MockReminder:
                mock_reminder_instance = MockReminder.return_value
                chatbot.set_reminder(user_id, "water", "HydrationReminder", MagicMock())
                mock_reminders.append(mock_reminder_instance)
        for reminder in mock_reminders:
            reminder.start.assert_called_once()
        assert mock_bot.send_message.call_count == num_users * 2


def test_run_bot():
    mock_bot = MagicMock()
    with patch.object(mock_bot, "polling") as mock_polling:
        run_bot(mock_bot)
        mock_polling.assert_called_once_with(non_stop=True)
    with patch.object(mock_bot, "polling", side_effect=KeyboardInterrupt):
        run_bot(mock_bot)
        if hasattr(mock_bot, "stop_polling"):
            mock_bot.stop_polling.assert_called()
