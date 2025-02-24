# P-Programist Telegram Bot #

P-Programist Telegram Bot is designed to streamline the process of registering for offline Python courses while offering additional features such as Python skill assessments, self-study references, and curated IT job vacancies. Built on an older version of Aiogram (pre-3.0), the bot leverages asynchronous programming and a modular structure to deliver a responsive and multi-language experience.


## Features ##
* Course Registration:

      Users can easily register for offline Python courses.

* Python Skill Assessment:

      The bot provides tests to evaluate a user’s Python level, ensuring they are well-prepared for the course.

* Self-Study References:

      Offers necessary references and resources to aid in self-study.

* Job Vacancy Dashboard:

      Scrapes local IT vacancy websites and displays available job opportunities directly in Telegram.

* Multi-Language Support:

      Primarily in Russian, with additional support for Kyrgyz and English.

* Interactive User Interface:

      Utilizes both inline keyboards and ReplyKeyboards for intuitive navigation.

## Built With

___Python 3.7+___

___Aiogram (pre-3.0 version)___

___Asyncio & uvloop for asynchronous operations___

___SQLAlchemy for database management___

___BeautifulSoup and related libraries for web scraping___


## Installation

#### Clone the repository:
```
git clone https://github.com/yourusername/P-Programist-Telegram-Bot.git
cd P-Programist-Telegram-Bot
```

#### Set up a virtual environment:
```
python3 -m venv venv
source venv/bin/activate  # On Windows use: venv\Scripts\activate
```

#### Install the dependencies:
```
pip install -r requirements.txt
```

#### Configure the Bot:
*   Set your Telegram Bot Token in the configuration file (typically in configs/core.py or via environment variables).


## Usage ##

To start the bot, simply run:

```python main.py```

The bot will start polling for updates and begin interacting with users on Telegram.


## Project Structure ##
```
P-Programist-Telegram-Bot/
├── buttons/
│   ├── inline_buttons.py      # Configurations for inline buttons
│   └── text_buttons.py        # Configurations for ReplyKeyboard buttons
├── configs/
│   ├── core.py                # Core configurations (keys, tokens, etc.)
│   ├── states.py              # Bot state definitions
│   └── subfunctions.py        # Helper functions and utilities
├── database/
│   ├── models.py              # Database models
│   └── settings.py            # Database connection settings
├── scrapers/
│   ├── local_scraper.py       # Scrapes local IT vacancies
│   └── upwork_scraper.py      # Scrapes vacancies from upwork.com
├── main.py                    # Main entry point of the bot
└── requirements.txt           # Project dependencies
```

## Testing ##

Note: Automated tests are currently in progress. You can perform manual testing by interacting with the bot on Telegram.

For contributors looking to add tests, here’s an example of how you might begin writing tests using pytest and Aiogram’s testing utilities:

```
import pytest
import asyncio
from main import dp, bot

@pytest.mark.asyncio
async def test_start_command():
    # Placeholder example: simulate /start command and check for a valid response.
    # Aiogram's test utilities can help simulate updates and messages.
    update = {}  # Create a fake update object for /start command
    # Implement further testing logic...
    assert True
```


### To run tests: ###
      
  1. Install pytest if you haven’t already:

    pip install pytest

  2. Run the tests:

    pytest

Contributions to expand and enhance the test suite are very welcome!

## Contributing ##

Contributions are encouraged!
If you have ideas or improvements, please submit a pull request or open an issue. The bot is designed to be infinitely extendable, so your input can help shape its future development.

## License ##

This project is licensed under the MIT License – see the LICENSE file for details.

### Acknowledgments ###

    Thanks to the Aiogram community for their robust framework and documentation.
    Gratitude to all contributors who help improve and maintain the project.