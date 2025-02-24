from aiogram.dispatcher.filters.state import StatesGroup, State

class BotStates(StatesGroup):
    set_language = State()
    main_menu = State()

    apply_for_course = State()
    set_course_time = State()
    confirm_number_for_applying = State()

    know_about_corses = State()
    read_about_company_text = State()

    vacancy_categories = State()
    company_vacancies = State()
    local_vacancies = State()
    bishkek_vacancies = State()
    foreign_vacancies = State()

    applied_for_vacancy = State()
    full_name_for_vacancy = State()
    cover_letter = State()
    github_link = State()
    confirm_number_for_vacancy = State()
    complete_vacancy_application = State()

    add_feedback = State()
    choose_times = State()
    feedback_text = State()
    more_detailed_vac = State()

    start_test = State()
    choose_answer = State()