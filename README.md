# Wellness and Reminder Telegram Bot
    #### Video Demo:  <https://youtu.be/PwdqjsL4Bq8>
    #### Description:
    The Wellness and Reminder Telegram Bot is a Python-based chatbot designed to encourage healthy habits and improve overall well-being. By sending regular reminders for hydration, stretching, and breaks, the bot helps users maintain a balanced routine during long work or study sessions. Users can customize the reminder intervals via a configuration file, making it adaptable to individual needs.

    Key Features

    Reminder System:
    Reminders for hydration, stretching, and breaks.
    Customizable intervals defined in config.json.

    Customizability:
    Personalize reminders by editing a JSON configuration file.

    Seamless Telegram Integration:
    Utilizes Telegram API for real-time message delivery.

    Thread Management:
    Background threads ensure reminders do not interfere with user interactions.

    Error Handling:
    Retry mechanism for message delivery ensures reliable functionality.

    Project Files

    project.py: Contains the main function and core logic of the bot, including:
    Reminder handling.
    User interaction.
    Telegram API integration.

    test_project.py: Includes tests for core functionality:
    Unit tests for load_config, initialize_bot, and run_bot.
    Integration tests for the bot's interaction with reminders.
    Performance tests to ensure stability under load.

    config.json: Defines default reminder intervals for hydration, stretching, and breaks.

    .env: Stores sensitive data like the Telegram bot token securely.

    requirements.txt: Lists dependencies, including libraries like python-telegram-bot.

    README.md: This document, providing an overview of the project.

    Future Enhancements
    Add advanced mental health check-ins and motivational messages.
    Create commands to allow users to customize reminders directly from the Telegram interface.
    Integrate analytics to track user health habits over time.



