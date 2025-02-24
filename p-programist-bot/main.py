# Standard library imports
from datetime import datetime, timedelta

# Third party imports
import aiogram
from aiogram import executor
from aiogram.bot import Bot
from aiogram.dispatcher import Dispatcher
from aiogram.types import Message, CallbackQuery, ParseMode, message
import asyncio
from asyncio.tasks import sleep
import uvloop

# SQL Alchemy
from sqlalchemy import exc, update, insert
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession

# Local application imports
from buttons.inlines_buttons import (
    Languages,
    MainMenu,
    Departments,
    GroupTime,
    ActiveVacancies,
    DepartmentFeedback,
    FeedbackSchedule,
    Quiz,
)
from buttons.text_buttons import ConfirmNumber
from configs import constants, states, subfunctions
from configs.core import redworker, storage, point, check, time_question, feedback_data
from database.settings import engine
from database.models import (
    Course,
    Customer,
    Feedback,
    Reception,
    Department,
    Vacancy,
    VacancyApplicants,
    TestQuestions,
    User,
    WorldVacancy
)

student_vr = ('1624089338')

uvloop.install()
loop = asyncio.get_event_loop()

bot = Bot(constants.PPROGRAMISTBOT_TOKEN, loop=loop)

dp = Dispatcher(bot=bot, loop=loop, storage=storage)


@dp.message_handler(commands=["start"], state="*")
async def start(message: Message):
    """
    The first function that the User interacts with.
    After the User pressed the /start command - he will be offered to choose a language for interaction.
    """
    async with AsyncSession(engine, expire_on_commit=False) as session:
        async with session.begin():
            all_users_for_check = select(User.chat_id)
            all_users_for_check = [i for i in await session.execute(all_users_for_check)]
            if (message['from']['id'],) in all_users_for_check:
                cmd = update(User).where(User.chat_id == message['from']['id']).values(
                    {
                        'current_page_on_vacancies':0
                    }
                )
                await session.execute(cmd)
                pass
            else:
                add_user = User(
                    chat_id = message['from']['id'],
                    username = message['from']['username'],
                    first_name = message['from']['first_name'],
                    last_name = message['from']['last_name']
                )
                session.add(add_user)
        await session.commit()
    await message.answer(
        text="%s | %s"
        % (
            constants.SPEECH["choose_language_ru"],
            constants.SPEECH["choose_language_kg"],
        ),
        reply_markup=Languages().lang_buttons(),
        parse_mode=ParseMode.MARKDOWN,
    )
    return await states.BotStates.set_language.set()


@dp.callback_query_handler(state=states.BotStates.set_language)
async def send_main_menu(call: CallbackQuery):
    """
    As soon as User set the most comfortable language,
    we send him buttons of main_menu and change Bot State.
    """
    chat_id = call.message.chat.id

    if call.data == "ru":
        await redworker.set_data(chat=chat_id, data="_ru")
        lang = await redworker.get_data(chat=chat_id)

        await call.message.edit_text(
            text=constants.SPEECH["main_menu" + lang],
            reply_markup=await MainMenu(chat_id).main_menu_buttons(str(chat_id) in student_vr),
            parse_mode=ParseMode.MARKDOWN,
        )
        return await states.BotStates.main_menu.set()

    elif call.data == "kg":
        await redworker.set_data(chat=chat_id, data="_kg")
        lang = await redworker.get_data(chat=chat_id)

        await call.message.edit_text(
            text=constants.SPEECH["main_menu" + lang],
            reply_markup=await MainMenu(chat_id).main_menu_buttons(str(chat_id) in student_vr),
            parse_mode=ParseMode.MARKDOWN,
        )
        return await states.BotStates.main_menu.set()


############################################################
######################## RECEPTION #########################
############################################################
@dp.callback_query_handler(state=states.BotStates.main_menu)
async def reception(call: CallbackQuery):
    """
    In case, User will be interested to continue,
    the bot will be monitoring which button has been pressed.
    This data is collecting for improving service and watch for users' interests.
    """
    chat_id = call.message.chat.id
    lang = await redworker.get_data(chat=chat_id)
    call_data = ('apply', 'about_courses', 'about_company', 'vacancies', 'feedback', 'test')

    if call.data in call_data:
        await subfunctions.increment_at_reception(Reception, call)

        if call.data == "apply":
            await call.message.edit_text(
                text=constants.SPEECH["choose_course" + lang],
                reply_markup=await Departments(chat_id).departments_buttons(back=True),
                parse_mode=ParseMode.MARKDOWN,
            )

            return await states.BotStates.apply_for_course.set()

        if call.data == "about_courses":
            await call.message.edit_text(
                text=constants.SPEECH["choose_course" + lang],
                reply_markup=await Departments(chat_id).departments_buttons(back=True),
                parse_mode=ParseMode.MARKDOWN,
            )

            return await states.BotStates.know_about_corses.set()

        if call.data == "about_company":
            reception_id = getattr(Reception, "id")

            reception = await subfunctions.object_exists(Reception, reception_id, 1)

            await call.message.edit_text(
                text=reception.about_company_text,
                reply_markup=await MainMenu(chat_id).step_back(),
                parse_mode=ParseMode.MARKDOWN,
            )

            return await states.BotStates.read_about_company_text.set()

        if call.data == "vacancies":
            await call.message.edit_text(
                text=constants.SPEECH["vacancy_category" + lang],
                reply_markup=await ActiveVacancies(chat_id).vacancies(),
                parse_mode=ParseMode.MARKDOWN,
            )

            return await states.BotStates.vacancy_categories.set()

        if call.data == "feedback":
            await call.message.edit_text(
                # text=constants.SPEECH["not_found" + lang],
                text=constants.SPEECH["changes" + lang],
                reply_markup=await DepartmentFeedback(chat_id).departments_buttons(),
                parse_mode=ParseMode.MARKDOWN,
            )
            await feedback_data.set_data(chat=chat_id, data=None)

            return await states.BotStates.add_feedback.set()

        if call.data == "test":
            await call.message.edit_text(
                text=constants.SPEECH["rules" + lang],
                reply_markup=await Quiz().rules(chat_id),
                parse_mode=ParseMode.MARKDOWN,
            )
            now = datetime.now()
            await time_question.set_data(chat=chat_id, data=(now.strftime("%H:%M:%S"), 1))
            await check.set_data(chat=chat_id, data=None)
            await point.set_data(chat=chat_id, data=None)

            return await states.BotStates.start_test.set()


@dp.message_handler(commands=["get_stats"], state="*")
async def stats(message: Message):
    """
    A secret feature available only to a select few. 
    Displays statistics on user clicks of buttons.
    """
    data = await subfunctions.get_stats()
    if message.chat.id in constants.SUPERUSERS:
        return await message.answer(
            text=f"""
Нажатий на клaвишу "Подать заявку"😎: {data['apply']}
Нажатий на клaвишу "О компании"🕍: {data['about_company']}
Нажатий на клaвишу "О курсах"🗿: {data['about_courses']}
Нажатий на клaвишу "Вакансии"🧹: {data['vacancies']}
"""
        )


############################################################
###################### END RECEPTION #######################
############################################################


############################################################
####################### APPLICATION ########################
############################################################
@dp.callback_query_handler(state=states.BotStates.apply_for_course)
async def set_time_for_course(call: CallbackQuery):
    """
    If the User pressed the "apply" button and wants to apply for a course,
    we find him in the database to see, whether he applied already within the last 3 days.
    This checking is made to avoid people flooding.
    If the User has already applied for a course, he can't apply again for the 3 following days.
    If the User is new we write him into the database to connect to him later.
    """

    if call.data:

        chat_id = call.message.chat.id
        lang = await redworker.get_data(chat=call.message.chat.id)

        # If User pressed "Back" button - return him to main menu
        if call.data == "back_to_menu":
            await call.message.edit_text(
                text=constants.SPEECH["main_menu" + lang],
                reply_markup=await MainMenu(chat_id).main_menu_buttons(str(chat_id) in student_vr),
                parse_mode=ParseMode.MARKDOWN,
            )

            return await states.BotStates.main_menu.set()

        attr = getattr(Customer, "chat_id")
        user = await subfunctions.object_exists(Customer, attr, chat_id)

        if user:
            time_range = timedelta(hours=24)
            if user.phone and user.updated_at + time_range > datetime.now():
                # If we find the User in database - that means he already applied for the last 3 days
                f_name, dp_name = user.first_name, user.department_name

                await call.message.edit_text(
                    text=constants.SPEECH["already_applied" + lang]
                    .replace("fn", f_name)
                    .replace("dp", dp_name),
                    parse_mode=ParseMode.MARKDOWN,
                )

                await asyncio.sleep(1.5)

                await call.message.answer(
                    text=constants.SPEECH["main_menu" + lang],
                    reply_markup=await MainMenu(chat_id).main_menu_buttons(str(chat_id) in student_vr),
                    parse_mode=ParseMode.MARKDOWN,
                )

                return await states.BotStates.main_menu.set()
            else:
                user_id = getattr(Customer, "id")
                department_name = " ".join(call.data.split("_")).title()

                await subfunctions.update_object(
                    Customer,
                    user_id,
                    user.id,
                    {
                        "department_name": department_name
                    }
                )

                await call.message.edit_text(
                    text=constants.SPEECH["choose_group_time" + lang],
                    reply_markup=await GroupTime(chat_id).group_time_buttons(),
                    parse_mode=ParseMode.MARKDOWN,
                )

                return await states.BotStates.set_course_time.set()
        else:
            """
            The function below is located in "configs.subfunctions" module.
            This function is responsible for operating user's applications for courses.
            """
            department_name = " ".join(call.data.split("_")).title()

            data = {
                "chat_id": chat_id,
                "first_name": call.from_user.first_name,
                "last_name": call.from_user.last_name
                if call.from_user.last_name is not None
                else "Unknown",
                "department_name": department_name,
            }

            await subfunctions.insert_object(Customer, data, call)

            await call.message.edit_text(
                text=constants.SPEECH["choose_group_time" + lang],
                reply_markup=await GroupTime(chat_id).group_time_buttons(),
                parse_mode=ParseMode.MARKDOWN,
            )

            return await states.BotStates.set_course_time.set()


@dp.callback_query_handler(state=states.BotStates.set_course_time)
async def confirm_number_to_apply(call: CallbackQuery):
    chat_id = call.message.chat.id
    lang = await redworker.get_data(chat=chat_id)
    if call.data and call.data.isdigit():
        attr = getattr(Customer, "chat_id")
        user = await subfunctions.object_exists(Customer, attr, chat_id)
        user_id = getattr(Customer, "id")

        await subfunctions.update_object(
            Customer, user_id, user.id, {"time": int(call.data)}
        )

        await call.message.edit_text(
            text=constants.SPEECH["confirm_to_apply" + lang],
            parse_mode=ParseMode.MARKDOWN,
        )

        await call.message.answer(
            text=constants.SPEECH["confirm_number_text" + lang],
            reply_markup=await ConfirmNumber(chat_id).confirm_number(),
            parse_mode=ParseMode.MARKDOWN,
        )

        return await states.BotStates.confirm_number_for_applying.set()

    elif call.data == 'back':
        await call.message.edit_text(
            text=constants.SPEECH["choose_course" + lang],
            reply_markup=await Departments(chat_id).departments_buttons(back=True),
            parse_mode=ParseMode.MARKDOWN,
        )

        return await states.BotStates.apply_for_course.set()


@dp.message_handler(
    content_types=["text", "contact"],
    state=states.BotStates.confirm_number_for_applying,
)
async def complete_applying(message: Message):
    chat_id = message.chat.id
    lang = await redworker.get_data(chat=chat_id)

    if message.contact:
        attr = getattr(Customer, "chat_id")
        user = await subfunctions.object_exists(Customer, attr, chat_id)
        user_id = getattr(Customer, "id")

        # In case if there will be some symbols other than digits we need to filter them
        await subfunctions.update_object(
            Customer,
            user_id,
            user.id,
            {
                "phone": int(
                    "".join(
                        [i for i in message.contact.phone_number if i.isdigit()])
                )
            },
        )

        await message.answer(
            text=constants.SPEECH["apllication_accepted" + lang],
            parse_mode=ParseMode.MARKDOWN,
        )

        # with open(constants.WELCOME_TO_THE_CLUB_BUDDY, "rb") as video:
        #     await message.answer_video(video=video)

        await message.answer(
            text=constants.SPEECH["main_menu" + lang],
            reply_markup=await MainMenu(chat_id).main_menu_buttons(str(chat_id) in student_vr),
            parse_mode=ParseMode.MARKDOWN,
        )

        return await states.BotStates.main_menu.set()
    else:
        await message.answer(
            text=constants.SPEECH["confirm_number_text" + lang],
            reply_markup=await ConfirmNumber(chat_id).confirm_number(ext=True),
            parse_mode=ParseMode.MARKDOWN,
        )

        return await states.BotStates.confirm_number_for_applying.set()


############################################################
##################### END APPLICATION ######################
############################################################


############################################################
###################### ABOUT COURSES #######################
############################################################
@dp.callback_query_handler(state=states.BotStates.know_about_corses)
async def send_information_about_course(call: CallbackQuery):
    chat_id = call.message.chat.id
    lang = await redworker.get_data(chat=chat_id)

    # The condition works when User clicked to the BACK button in the main menu
    if call.data == "back_to_menu":
        await call.message.edit_text(
            text=constants.SPEECH["main_menu" + lang],
            reply_markup=await MainMenu(chat_id).main_menu_buttons(str(chat_id) in student_vr),
            parse_mode=ParseMode.MARKDOWN,
        )

        return await states.BotStates.main_menu.set()

    # The condition works when User clicked to the BACK button from Departments
    elif call.data == "back":
        await call.message.edit_text(
            text=constants.SPEECH["choose_course" + lang],
            reply_markup=await Departments(chat_id).departments_buttons(back=True),
            parse_mode=ParseMode.MARKDOWN,
        )

        return await states.BotStates.know_about_corses.set()

    if call.data:
        # Get an attrubute of Department model
        dp_field = getattr(Department, "department_name")

        # Edit callback_data into database value
        dp_name = " ".join(call.data.split("_")).title()

        # Retrieve department object from database by "department_name"
        dp = await subfunctions.object_exists(Department, dp_field, dp_name)

        # Get an attrubute of Course model
        course_field = getattr(Course, "department_id")

        # Here might be an ERROR in case if database will be empty
        # Retrieve course object from database by "department_id"
        course = await subfunctions.object_exists(Course, course_field, dp.id)

        if not course:
            await call.message.edit_text(
                text=constants.SPEECH["course_under_development" + lang],
                reply_markup=await MainMenu(chat_id).main_menu_buttons(str(chat_id) in student_vr),
                parse_mode=ParseMode.MARKDOWN,
            )

            return await states.BotStates.main_menu.set()

        await call.message.edit_text(
            text=course.department_info,
            reply_markup=await MainMenu(chat_id).step_back(),
            parse_mode=ParseMode.MARKDOWN,
        )

        return await states.BotStates.know_about_corses.set()


############################################################
#################### END ABOUT COURSES #####################
############################################################


############################################################
###################### ABOUT COMPANY #######################
############################################################
@dp.callback_query_handler(state=states.BotStates.read_about_company_text)
async def read_about_company(call: CallbackQuery):
    chat_id = call.message.chat.id
    lang = await redworker.get_data(chat=chat_id)

    # If User pressed "Back" button - return him to main menu
    if call.data:
        await call.message.edit_text(
            text=constants.SPEECH["main_menu" + lang],
            reply_markup=await MainMenu(chat_id).main_menu_buttons(str(chat_id) in student_vr),
            parse_mode=ParseMode.MARKDOWN,
        )

        return await states.BotStates.main_menu.set()


############################################################
#################### END ABOUT COMPANY #####################
############################################################


############################################################
######################## VACANCIES #########################
############################################################
@dp.callback_query_handler(state=states.BotStates.vacancy_categories)
async def vacancy_list(call: CallbackQuery):
    """
    Эта функция занимается выводом вакансий.
    Есть 3 условия, отвечающие за соответствующие данные из соответствующих таблиц(BishkekVacancy etc...).
    1.
    2. Условие 'city' отвечает за вывод вакансий по городу. 
    Оно вызывает асинхронную функцию subfunctions.extract_bishkek_vacancies, 
    формирует сообщение и отправляет его пользователю.
    3.
    """
    chat_id = call.message.chat.id
    lang = await redworker.get_data(chat=chat_id)

    if call.data == "back_to_menu":
        await call.message.edit_text(
            text=constants.SPEECH["main_menu" + lang],
            reply_markup=await MainMenu(chat_id).main_menu_buttons(str(chat_id) in student_vr),
            parse_mode=ParseMode.MARKDOWN,
        )

        return await states.BotStates.main_menu.set()

    if call.data == 'city':
        vacancies_list = await subfunctions.extract_bishkek_vacancies()
        [(await call.message.answer(text=f"""
💻 Должность:  {text[0]}\n
🕴 Работодатель: {text[5]}\n
💲 Зарплата: {text[1]}\n\n

{text[2][:330]}...\n\n
🧠 Требуемый опыт работы: {text[3]}\n
🕙 Занятость: {text[4]}\n
        """)) for text in vacancies_list]
        await states.BotStates.local_vacancies.set()

        return await call.message.answer(
           text=constants.SPEECH["back_to_vacancies" + lang],
           reply_markup=await MainMenu(chat_id).step_back(),
           parse_mode=ParseMode.MARKDOWN)

    elif call.data == 'foreign':
        await call.message.edit_text(
           text='Выберите ЯП:',
           reply_markup=await ActiveVacancies(chat_id).choose_foreign_vacancies_type(),
           parse_mode=ParseMode.MARKDOWN)

        await states.BotStates.foreign_vacancies.set()

    


@dp.callback_query_handler(state=states.BotStates.foreign_vacancies)
async def foreign_vacancy_list(call: CallbackQuery):
    """
    Вывод мировых вакансий по питону и джаваскрипту
    """
    lang = await redworker.get_data(chat=call.message.chat.id)
    if call.data == 'back_to_vacancies':
        await call.message.edit_text(
                text=constants.SPEECH["vacancy_category" + lang],
                reply_markup=await ActiveVacancies(call.message.chat.id).vacancies(),
                parse_mode=ParseMode.MARKDOWN,
            )
        async with AsyncSession(engine, expire_on_commit=False) as session:
            async with session.begin():
                cmd = update(User).where(User.chat_id == call.message['chat']['id']).values(
                        {
                            'current_page_on_vacancies':0
                        }
                    )
                await session.execute(cmd)
            await session.commit()
        return await states.BotStates.vacancy_categories.set()

    elif call.data == 'more':
        await bot.edit_message_reply_markup(chat_id = call.message.chat.id, message_id = call.message.message_id, reply_markup=None)
        async with AsyncSession(engine, expire_on_commit=False) as session:
            async with session.begin():
                step = select(User.current_page_on_vacancies).where(User.chat_id == int(call.message['chat']['id']))
                step = await session.execute(step)
                step = step.fetchall()[0][0]
                vacancies_list = await subfunctions.extract_world_vacancies('JavaScript', step)
                if len(vacancies_list) >= 10:
                    [(await call.message.answer(text=f"""
    Вакансия: {text[0]}\n
    Плата: {text[1]}\n
    Тех. задание: {text[2][:350]}...\n
    Тэги: {text[3]}\n
    Дата заказа: {text[4][:10]} числа в {text[4][12:19]}\n
    Ссылка на проект:{text[5]}
            """)) for text in vacancies_list]
                    
                    cmd = update(User).where(User.chat_id == call.message['chat']['id']).values(
                        {
                            'current_page_on_vacancies':step+1
                        }
                    )
                    await session.execute(cmd)
                else:
                    cmd = update(User).where(User.chat_id == call.message['chat']['id']).values(
                        {
                            'current_page_on_vacancies':0
                        }
                    )
                    await session.execute(cmd)
                    await call.message.answer(
                            text='Вакансии закончились:(',
                            reply_markup=await ActiveVacancies(call.message['chat']['id']).vacancies_are_over(),
                            parse_mode=ParseMode.MARKDOWN)
                    return await session.commit()


        
    elif call.data == 'javascript':
        await bot.edit_message_reply_markup(chat_id = call.message.chat.id, message_id = call.message.message_id, reply_markup=None)
        vacancies_list = await subfunctions.extract_world_vacancies('JavaScript')
        [(await call.message.answer(text=f"""
Вакансия: {text[0]}\n
Плата: {text[1]}\n
Тех. задание: {text[2][:350]}...\n
Тэги: {text[3]}\n
Дата заказа: {text[4][:10]} числа в {text[4][12:19]}\n
Ссылка на проект:{text[5]}
        """)) for text in vacancies_list]
        

    elif call.data == 'python':
        await bot.edit_message_reply_markup(chat_id = call.message.chat.id, message_id = call.message.message_id, reply_markup=None)
        vacancies_list = await subfunctions.extract_world_vacancies('Python')
        [(await call.message.answer(text=f"""
Вакансия: {text[0]}\n
Плата: {text[1]}\n
Тех. задание: {text[2][:350]}...\n
Тэги: {text[3]}\n
Дата заказа: {text[4][:10]} числа в {text[4][12:19]}\n
Ссылка на проект:{text[5]}
        """)) for text in vacancies_list]
    

    return await call.message.answer(
           text='Еще вакансии:',
           reply_markup=await ActiveVacancies(call.message['chat']['id']).more_vacancies(),
           parse_mode=ParseMode.MARKDOWN)

   
    if call.data == "back":
        await call.message.edit_text(
            text=constants.SPEECH["main_menu" + lang],
            reply_markup=await MainMenu(chat_id).main_menu_buttons(str(chat_id) in student_vr),
            parse_mode=ParseMode.MARKDOWN,
        )

        return await states.BotStates.main_menu.set()

    else:
        vacancies_more = await subfunctions.more_text(call, call.data)
        [(await call.message.edit_text(text=f"""
    💻 Должность:  {text[0]}\n
    🕴 Работодатель: {text[5]}\n
    💲 Зарплата: {text[1]}\n\n
    {text[2][:330]}...\n\n
    🧠 Требуемый опыт работы: {text[3]}\n
    🕙 Занятость: {text[4]}\n
            """)) for text in vacancies_more]


@dp.callback_query_handler(state=states.BotStates.local_vacancies)
async def vacancies_list_provided(call: CallbackQuery):
    chat_id = call.message.chat.id
    lang = await redworker.get_data(chat=chat_id)

    if call.data == "back":
        await call.message.edit_text(
            text=constants.SPEECH["vacancy_category" + lang],
            reply_markup=await ActiveVacancies(chat_id).vacancies(),
            parse_mode=ParseMode.MARKDOWN,
        )

        return await states.BotStates.vacancy_categories.set()

    chat_id_attr = getattr(VacancyApplicants, "chat_id")
    applicant = await subfunctions.object_exists(
        VacancyApplicants, chat_id_attr, chat_id
    )

    if applicant:
        if applicant.phone_number:
            await call.message.answer(
                text=constants.SPEECH["already_applied_for_vacancy" + lang],
                parse_mode=ParseMode.MARKDOWN,
            )

            await asyncio.sleep(1.5)

            await call.message.answer(
                text=constants.SPEECH["main_menu" + lang],
                reply_markup=await MainMenu(chat_id).main_menu_buttons(str(chat_id) in student_vr),
                parse_mode=ParseMode.MARKDOWN,
            )

            return await states.BotStates.main_menu.set()

    data = {
        "vacancy_id": int(call.data),
        "chat_id": chat_id,
    }

    await subfunctions.insert_object(VacancyApplicants, data, call)

    await call.message.answer(
        text=constants.SPEECH["tell_me_full_name" +
                              lang], parse_mode=ParseMode.MARKDOWN
    )

    return await states.BotStates.full_name_for_vacancy.set()


@dp.message_handler(
    content_types=["text"], state=states.BotStates.full_name_for_vacancy
)
async def ask_fullname_for_vacancy(message: Message):
    chat_id = message.chat.id
    lang = await redworker.get_data(chat=chat_id)

    chat_id_attr = getattr(VacancyApplicants, "chat_id")
    await subfunctions.update_object(
        VacancyApplicants, chat_id_attr, chat_id, {"full_name": message.text}
    )

    await message.answer(
        text=constants.SPEECH["cover_letter" +
                              lang], parse_mode=ParseMode.MARKDOWN
    )

    return await states.BotStates.cover_letter.set()


@dp.message_handler(content_types=["text"], state=states.BotStates.cover_letter)
async def ask_cover_letter_for_vacancy(message: Message):
    chat_id = message.chat.id
    lang = await redworker.get_data(chat=chat_id)

    chat_id_attr = getattr(VacancyApplicants, "chat_id")
    await subfunctions.update_object(
        VacancyApplicants, chat_id_attr, chat_id, {
            "cover_letter": message.text}
    )

    await message.answer(
        text=constants.SPEECH["provide_github" +
                              lang], parse_mode=ParseMode.MARKDOWN
    )

    return await states.BotStates.github_link.set()


@dp.message_handler(content_types=["text"], state=states.BotStates.github_link)
async def ask_github_link_for_vacancy(message: Message):
    chat_id = message.chat.id
    lang = await redworker.get_data(chat=chat_id)

    if 'github' in message.text or 'bitbucket' in message.text:
        chat_id_attr = getattr(VacancyApplicants, "chat_id")
        await subfunctions.update_object(
            VacancyApplicants, chat_id_attr, chat_id, {
                "github_link": message.text}
        )

        await message.answer(
            text=constants.SPEECH["confirm_to_apply" +
                                lang], parse_mode=ParseMode.MARKDOWN
        )



        await message.answer(
            text=constants.SPEECH["confirm_number_text" + lang],
            reply_markup=await ConfirmNumber(chat_id).confirm_number(),
            parse_mode=ParseMode.MARKDOWN,
        )

        return await states.BotStates.confirm_number_for_vacancy.set()

    else:
        await message.answer(
            text=constants.SPEECH["provide_github" +
                                  lang], parse_mode=ParseMode.MARKDOWN
        )
        return await states.BotStates.github_link.set()


@dp.message_handler(
    content_types=["text", "contact"], state=states.BotStates.confirm_number_for_vacancy
)
async def complete_vacancy_applying(message: Message):
    chat_id = message.chat.id
    lang = await redworker.get_data(chat=chat_id)

    if message.contact:
        chat_id_attr = getattr(VacancyApplicants, "chat_id")
        await subfunctions.update_object(
            VacancyApplicants,
            chat_id_attr,
            chat_id,
            {
                "phone_number": int(
                    "".join(
                        [i for i in message.contact.phone_number if i.isdigit()])
                )
            },
        )

        await message.answer(
            text=constants.SPEECH["apllication_accepted" + lang],
            parse_mode=ParseMode.MARKDOWN,
        )

        await asyncio.sleep(1.7)

        await message.answer(
            text=constants.SPEECH["main_menu" + lang],
            reply_markup=await MainMenu(chat_id).main_menu_buttons(str(chat_id) in student_vr),
            parse_mode=ParseMode.MARKDOWN,
        )

        return await states.BotStates.main_menu.set()

    await message.answer(
        text=constants.SPEECH["confirm_to_apply" + lang],
        reply_markup=await ConfirmNumber(chat_id).confirm_number(),
        parse_mode=ParseMode.MARKDOWN,
    )

    return await states.BotStates.confirm_number_for_vacancy.set()


############################################################
###################### END VACANCIES #######################
############################################################

############################################################
######################## FEEDBACKS #########################
############################################################
@dp.callback_query_handler(state=states.BotStates.add_feedback)
async def check_group(call: CallbackQuery):
    chat_id = call.message.chat.id
    lang = await redworker.get_data(chat=chat_id)

    if call.data == "back":
        await call.message.edit_text(
            text=constants.SPEECH["main_menu" + lang],
            reply_markup=await MainMenu(chat_id).main_menu_buttons(str(chat_id) in student_vr),
            parse_mode=ParseMode.MARKDOWN,
        )
        return await states.BotStates.main_menu.set()

    if call.data == "python2":
        await feedback_data.set_data(chat=chat_id, data=(chat_id, 1, 'groups', call.message.chat.first_name, call.message.chat.last_name, 'f_text'))
    elif call.data == "javascript2":
        await feedback_data.set_data(chat=chat_id, data=(chat_id, 3, 'groups', call.message.chat.first_name, call.message.chat.last_name, 'f_text'))

    await call.message.edit_text(
        text=constants.SPEECH["changes_time" + lang],
        reply_markup=await FeedbackSchedule(chat_id).group_times(),
        parse_mode=ParseMode.MARKDOWN,
    )
    return await states.BotStates.choose_times.set()


@dp.callback_query_handler(state=states.BotStates.choose_times)
async def choose_times_gr(call: CallbackQuery):
    chat_id = call.message.chat.id
    lang = await redworker.get_data(chat=chat_id)
    feedback_tb = await feedback_data.get_data(chat=chat_id)

    if call.data == "0":
        await feedback_data.set_data(chat=chat_id, data=(feedback_tb[0], feedback_tb[1], 0, feedback_tb[3], feedback_tb[4], 'f_text'))
    elif call.data == "1":
        await feedback_data.set_data(chat=chat_id, data=(feedback_tb[0], feedback_tb[1], 1, feedback_tb[3], feedback_tb[4], 'f_text'))

    await call.message.edit_text(
        text=constants.SPEECH["feedback" + lang],
        parse_mode=ParseMode.MARKDOWN,
    )
    return await states.BotStates.feedback_text.set()


@dp.message_handler(content_types=["text"], state=states.BotStates.feedback_text)
async def feedback_text(message: Message):
    chat_id = message.chat.id
    lang = await redworker.get_data(chat=chat_id)
    feedback_tb = await feedback_data.get_data(chat=chat_id)

    await feedback_data.set_data(chat=chat_id, data=(feedback_tb[0], feedback_tb[1], feedback_tb[2], feedback_tb[3], feedback_tb[4], message.text))
    data_in_tables = await feedback_data.get_data(chat=chat_id)

    data = {
        "telegram_id": str(data_in_tables[0]),
        "department_id": data_in_tables[1],
        "groups": data_in_tables[2],
        "first_name": data_in_tables[3],
        "last_name": data_in_tables[4] if data_in_tables[4] else '',
        "feedback_text": data_in_tables[5],
    }

    await subfunctions.insert_feedback(Feedback, data)

    await message.answer(
        text=f'{constants.SPEECH["feedback_answer" + lang]} \n{constants.SPEECH["main_menu" + lang]}',
        reply_markup=await MainMenu(chat_id).main_menu_buttons(str(chat_id) in student_vr),
        parse_mode=ParseMode.MARKDOWN,
    )
    return await states.BotStates.main_menu.set()

############################################################
###################### END FEEDBACKS #######################
############################################################

############################################################
########################## TESTS ###########################
############################################################


@dp.callback_query_handler(state=states.BotStates.start_test)
async def questions(call: CallbackQuery):
    '''В этой функции отправляются вопросы и записываются в БД ответы пользователей, 
    далее отправляет это данные в следущую функцию.'''

    chat_id = call.message.chat.id
    lang = await redworker.get_data(chat=chat_id)
    checking = await check.get_data(chat=chat_id)
    time_question_id = await time_question.get_data(chat=chat_id)

    if call.data == "back" or call.data == "stop_test":
        await call.message.edit_text(
            text=constants.SPEECH["main_menu" + lang],
            reply_markup=await MainMenu(chat_id).main_menu_buttons(str(chat_id) in student_vr),
            parse_mode=ParseMode.MARKDOWN,
        )
        return await states.BotStates.main_menu.set()

    now = datetime.now()
    current_time = now.strftime("%H:%M:%S")
    times = str(datetime.strptime(current_time, constants.TYPE_TIME) -
                datetime.strptime(time_question_id[0], constants.TYPE_TIME))

    if datetime.strptime(times, constants.TYPE_TIME) > datetime.strptime(constants.TIME_LIMIT, constants.TYPE_TIME):
        await call.message.edit_text(
            text=f'{constants.SPEECH["time_stop" + lang]} \n{constants.SPEECH["main_menu" + lang]}',
            reply_markup=await MainMenu(chat_id).main_menu_buttons(str(chat_id) in student_vr),
            parse_mode=ParseMode.MARKDOWN,
        )
        return await states.BotStates.main_menu.set()

    if time_question_id[1] <= 10:
        questions_list = await subfunctions.questions(call, time_question_id[1])
        generat = next(questions_list)

        if not call.data == 'start_test':
            if checking:
                await check.set_data(chat=chat_id, data=f'{checking}, {call.data}')
            else:
                await check.set_data(chat=chat_id, data=f'{call.data}')

        await call.message.edit_text(
            text=generat[0],
            reply_markup=await Quiz().choose_true_answers(chat_id, generat[1].split(', ')),
            parse_mode=ParseMode.MARKDOWN
        )

        await time_question.set_data(chat=chat_id, data=(time_question_id[0], 1+time_question_id[1]))
    else:
        await check.set_data(chat=chat_id, data=f'{checking}, {call.data}')

        return await states.BotStates.choose_answer.set()
    return await states.BotStates.start_test.set()


@dp.callback_query_handler(state=states.BotStates.choose_answer)
async def check_questions(call: CallbackQuery):
    '''В этой функции проверяется правильно ли он ответил на тот или иной вопрос, 
    далее все баллы подсчитиваютя и отправляются пользователю.'''

    chat_id = call.message.chat.id
    lang = await redworker.get_data(chat=chat_id)
    checking = await check.get_data(chat=chat_id)

    for question_id in range(1, 11):
        questions_list = await subfunctions.questions(call, question_id)
        generat = next(questions_list)
        if generat[2] == checking.split(', ')[question_id-1]:
            points = await point.get_data(chat=chat_id)
            if points:
                await point.set_data(chat=chat_id, data=points+generat[3])
            else:
                await point.set_data(chat=chat_id, data=generat[3])

    await call.message.edit_text(
        text=f'Ваш результат: {await point.get_data(chat=chat_id) if await point.get_data(chat=chat_id) else 0} баллов! \n{constants.SPEECH["main_menu" + lang]}',
        reply_markup=await MainMenu(chat_id).main_menu_buttons(str(chat_id) in student_vr),
        parse_mode=ParseMode.MARKDOWN,
    )
    return await states.BotStates.main_menu.set()


############################################################
######################## END TESTS #########################
############################################################

if __name__ == "__main__":
    executor.start_polling(dispatcher=dp, loop=loop)
