# Wellness & Reminder Bot

**Video demo:** https://youtu.be/PwdqjsL4Bq8  

This is my **CS50P Final Project**.  
It’s a simple Telegram bot that helps users take care of themselves during long study or work sessions.  
The bot sends reminders to drink water, stretch, and take breaks.  
Users can set their own reminder intervals by editing a small config file.

---

## 🔍 Features
- Regular reminders (hydration, stretching, rest).  
- Customizable schedule via `config.json`.  
- Works directly in Telegram using the official API.  
- Runs in the background without blocking chats.  
- Error handling with retry mechanism for reliable delivery.  

---

## 🧰 Tech Stack
- Python
- python-telegram-bot
- JSON configuration

---

## 🚀 How to Run
1. Clone this repo.
2. Install dependencies:
pip install -r requirements.txt
3. Add your Telegram Bot API token in .env.
4. Start the bot:
python project.py

---

👩‍💻 **Author:** Viktorija Zviedrāne  
*CS50x Final Project, December 2024*

