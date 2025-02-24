from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from configs.constants import SPEECH
from configs.core import redworker


class ConfirmNumber(object):
    """This class is only responsible for generating one sigle button for Phone number confirmation."""

    def __init__(self, chat_id):
        super(ConfirmNumber, self).__init__()
        self.chat_id = chat_id
        self.markup = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)

    async def confirm_number(self, ext=False):
        lang = await redworker.get_data(chat=self.chat_id)

        phone = KeyboardButton(
            text=SPEECH["confirm_number_btn" + lang], request_contact=True
        )

        cancel = KeyboardButton(text=SPEECH["cancel" + lang])

        self.markup.add(phone)

        if ext:
            self.markup.add(cancel)

        return self.markup
