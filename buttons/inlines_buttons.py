from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from configs.constants import SPEECH
from configs.core import redworker


class Languages(object):
    """Languages class is responsible for generating buttons for choosing language."""

    def __init__(self):
        super(Languages, self).__init__()
        self.markup = InlineKeyboardMarkup(row_width=2)

    def lang_buttons(self):
        ru_btn = InlineKeyboardButton("Русский 🇷🇺", callback_data="ru")

        kg_btn = InlineKeyboardButton("English 🇺🇸", callback_data="kg")

        self.markup.add(ru_btn, kg_btn)

        return self.markup


class MainMenu(object):
    """This class is responsible for Inline buttons after You choose the language."""

    def __init__(self, chat_id):
        super(MainMenu, self).__init__()
        self.markup = InlineKeyboardMarkup(row_width=2)

        self.chat_id = chat_id

    async def main_menu_buttons(self, shows):
        """
        Method accepts one primary argument that hides some buttons for authentication reasons.
        Also, the method generates all buttons regarding to the main menu.
        """
        lang = await redworker.get_data(chat=self.chat_id)

        apply_btn = InlineKeyboardButton(
            text=SPEECH["apply" + lang], callback_data="apply"
        )

        about_courses = InlineKeyboardButton(
            text=SPEECH["about_courses" + lang], callback_data="about_courses"
        )

        about_company = InlineKeyboardButton(
            text=SPEECH["about_company_btn" + lang], callback_data="about_company"
        )

        vacancies = InlineKeyboardButton(
            text=SPEECH["vacancies" + lang], callback_data="vacancies"
        )

        feedback = InlineKeyboardButton(
            text=SPEECH["feedback_btn" + lang], callback_data="feedback"
        )

        tests = InlineKeyboardButton(
            text=SPEECH["test_btn" + lang], callback_data="test"
        )

        self.markup.add(apply_btn, about_courses, about_company, vacancies, tests)
        if shows == True:
            self.markup.add(feedback)

        return self.markup

    async def step_back(self):
        """
        This single method is responsible for button that returns to one step back!
        """
        lang = await redworker.get_data(chat=self.chat_id)

        markup = InlineKeyboardMarkup(row_width=2)

        back = InlineKeyboardButton(text=SPEECH["back" + lang], callback_data="back")

        markup.add(back)

        return markup


class Departments(object):
    """The object keeps all buttons that relates to Programming languages buttons."""

    def __init__(self, chat_id):
        super(Departments, self).__init__()
        self.chat_id = chat_id
        self.markup = InlineKeyboardMarkup(row_width=1)

    async def departments_buttons(self, back=False):
        lang = await redworker.get_data(chat=self.chat_id)

        python = InlineKeyboardButton(text="Python 🐍", callback_data="python")

        sys_admin = InlineKeyboardButton(
            text="Системный администратор ⚙️", callback_data="system_administrator"
        )

        javascript = InlineKeyboardButton(
            text="JavaScript 👨‍🎨", callback_data="javascript"
        )

        java = InlineKeyboardButton(text="Java ⚒", callback_data="java")

        back_btn = InlineKeyboardButton(
            text=SPEECH["back" + lang], callback_data="back_to_menu"
        )

        self.markup.add(
            python,
            sys_admin,
            javascript,
            java,
        )

        if back:
            self.markup.add(back_btn)

        return self.markup


class GroupTime(object):
    """docstring for GroupTime."""

    def __init__(self, chat_id):
        super(GroupTime, self).__init__()

        self.chat_id = chat_id
        self.markup = InlineKeyboardMarkup(row_width=2)

    async def group_time_buttons(self):
        lang = await redworker.get_data(chat=self.chat_id)

        morning = InlineKeyboardButton(
            text=SPEECH["morning_group" + lang], callback_data=0
        )

        evening = InlineKeyboardButton(
            text=SPEECH["evening_group" + lang], callback_data=1
        )

        back_btn = InlineKeyboardButton(
            text=SPEECH["back" + lang],
            callback_data='back'
        )

        self.markup.add(morning, evening, back_btn)

        return self.markup


class ActiveVacancies(object):
    def __init__(self, chat_id):
        super(ActiveVacancies, self).__init__()
        self.chat_id = chat_id

    async def vacancies(self):
        markup = InlineKeyboardMarkup(row_width=1)
        lang = await redworker.get_data(chat=self.chat_id)

        company = InlineKeyboardButton(
            text=SPEECH["company_vacancies" + lang], callback_data="company"
        )

        city = InlineKeyboardButton(
            text=SPEECH["city_vacancies" + lang], callback_data="city"
        )

        foreign = InlineKeyboardButton(
            text=SPEECH["foreign_vacancies" + lang], callback_data="foreign"
        )

        back_btn = InlineKeyboardButton(
            text=SPEECH["back" + lang], callback_data="back_to_menu"
        )

        markup.add(company, city, foreign, back_btn)

        return markup

    async def more_for_vacancy(self, vacancy_id):
        markup = InlineKeyboardMarkup(row_width=1)
        lang = await redworker.get_data(chat=self.chat_id)

        more = InlineKeyboardButton(
            text=SPEECH["more_detailed_btn" + lang],
            callback_data=vacancy_id
        )

        markup.add(more)
        return markup
    
    async def choose_foreign_vacancies_type(self):
        markup = InlineKeyboardMarkup(row_width=1)
        lang = await redworker.get_data(chat=self.chat_id)


        javascript = InlineKeyboardButton(
            text='JavaScript',
            callback_data='javascript'
        )


        python = InlineKeyboardButton(
            text='Python',
            callback_data='python'
        )


        back_btn = InlineKeyboardButton(
            text=SPEECH["back" + lang],
            callback_data='back_to_vacancies'
        )

        markup.add(
            javascript, python
        )
        markup.add(
            back_btn
        )

        return markup

    async def more_vacancies(self):
        markup = InlineKeyboardMarkup(row_width=1)
        lang = await redworker.get_data(chat=self.chat_id)


        more = InlineKeyboardButton(
            text='Ещё вакансии',
            callback_data='more'
        )


        back_btn = InlineKeyboardButton(
            text=SPEECH["back" + lang],
            callback_data='back_to_vacancies'
        )

        markup.add(
            more,
            back_btn
        )
        return markup


    async def vacancies_are_over(self):
        markup = InlineKeyboardMarkup(row_width=1)
        lang = await redworker.get_data(chat=self.chat_id)

        back_btn = InlineKeyboardButton(
            text=SPEECH["back" + lang],
            callback_data='back_to_vacancies'
        )

        markup.add(
            back_btn
        )
        return markup



    async def apply_for_vacancy(self, vacancy_id):
        markup = InlineKeyboardMarkup(row_width=1)
        lang = await redworker.get_data(chat=self.chat_id)

        apply = InlineKeyboardButton(
            text=SPEECH["apply_for_vacancy" + lang], callback_data=vacancy_id
        )

        markup.add(apply)

        return markup


class DepartmentFeedback(object):
    """docstring for DepartmentFeedback."""

    def __init__(self, chat_id):
        super(DepartmentFeedback, self).__init__()
        self.chat_id = chat_id
        self.markup = InlineKeyboardMarkup(row_width=2)

    async def departments_buttons(self):
        lang = await redworker.get_data(chat=self.chat_id)

        python = InlineKeyboardButton(text="Python 🐍", callback_data="python2")

        javascript = InlineKeyboardButton(
            text="JavaScript 👨‍🎨", callback_data="javascript2"
        )

        back = InlineKeyboardButton(text=SPEECH["back" + lang], callback_data="back")

        self.markup.add(python, javascript, back)

        return self.markup


class FeedbackSchedule(object):
    """docstring for FeedbackSchedule."""

    def __init__(self, chat_id):
        super(FeedbackSchedule, self).__init__()
        self.chat_id = chat_id
        self.markup = InlineKeyboardMarkup(row_width=2)

    async def group_times(self):
        lang = await redworker.get_data(chat=self.chat_id)

        morning = InlineKeyboardButton(
            text=SPEECH["morning_group" + lang], callback_data=0
        )

        evening = InlineKeyboardButton(
            text=SPEECH["evening_group" + lang], callback_data=1
        )

        back = InlineKeyboardButton(text=SPEECH["back" + lang], callback_data="back")

        self.markup.add(morning, evening, back)

        return self.markup


class Quiz(object):
    """docstring for Test."""

    def __init__(self):
        super(Quiz, self).__init__()

    async def rules(self, chat_id):
        lang = await redworker.get_data(chat=chat_id)
        markup = InlineKeyboardMarkup(row_width=1)

        start_test = InlineKeyboardButton(
            text=SPEECH["start_test_btn" + lang], callback_data="start_test"
        )

        back = InlineKeyboardButton(text=SPEECH["back" + lang], callback_data="back")

        markup.add(start_test, back)
        return markup

    async def choose_true_answers(self, chat_id, answers):
        lang = await redworker.get_data(chat=chat_id)
        markup = InlineKeyboardMarkup(row_width=2)

        answer1 = InlineKeyboardButton(text=answers[0], callback_data="1")
        answer2 = InlineKeyboardButton(text=answers[1], callback_data="2")
        answer3 = InlineKeyboardButton(text=answers[2], callback_data="3")
        answer4 = InlineKeyboardButton(text=answers[3], callback_data="4")
        stop_tests = InlineKeyboardButton(
            text=SPEECH["stop_test_btn" + lang], callback_data="stop_test"
        )

        markup.add(answer1, answer2, answer3, answer4, stop_tests)
        return markup

    async def know_points(self, chat_id):
        lang = await redworker.get_data(chat=chat_id)
        markup = InlineKeyboardMarkup(row_width=1)

        know = InlineKeyboardButton(
            text=SPEECH["know_point_btn" + lang], callback_data="knows"
        )

        markup.add(know)
        return markup
