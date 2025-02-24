"""The module is responsible for tables and relations betweeen them inside of the database."""
# Standard library imports
import datetime

# Third party imports
from sqlalchemy import (
    Column,
    ForeignKey,
    Integer,
    String,
    TIMESTAMP,
    SmallInteger,
    BigInteger,
    Text,
)

from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql.expression import delete, insert
from sqlalchemy.sql.functions import current_date
from sqlalchemy.sql.sqltypes import TEXT, VARCHAR, Boolean


# Local application imports
from database.settings import engine

from configs.constants import (
    PYTHON_INFO_TEXT_RU,
    PYTHON_INFO_TEXT_KG,
    SYS_ADMIN_INFO_TEXT_RU,
    SYS_ADMIN_INFO_TEXT_KG,
    JAVASCRIPT_INFO_TEXT_RU,
    JAVASCRIPT_INFO_TEXT_KG,
    JAVA_INFO_TEXT_RU,
    JAVA_INFO_TEXT_KG,
    ABOUT_COMPANY_RU,
    ABOUT_COMPANY_KG,
    QUESTIONS,
)

Base = declarative_base()


class BaseModel(Base):
    __abstract__ = True

    id = Column(
        Integer, nullable=False, unique=True, primary_key=True, autoincrement=True
    )

    created_at = Column(
        TIMESTAMP,
        nullable=False,
        # It is forbidden to leave just -> datetime.datetime.now convert it to str first!
        server_default=str(datetime.datetime.now()),
        comment="The date an object has been created",
    )

    updated_at = Column(
        TIMESTAMP,
        nullable=False,
        server_default=str(datetime.datetime.now()),
        onupdate=datetime.datetime.now,
        comment="The date an object has been updated",
    )

    def __repr__(self):
        return "<{0.__class__.__name__}(id={0.id!r})>".format(self)


class Reception(BaseModel):
    __tablename__ = "reception"

    apply = Column(
        Integer,
        nullable=False,
        comment="How much times the APPLY button has been pressed",
        default=1,
    )

    about_courses = Column(
        BigInteger,
        nullable=False,
        comment="How much times the ABOUT_COURSES button has been pressed",
        default=1,
    )

    about_company = Column(
        Integer,
        nullable=False,
        comment="How much times the ABOUT_COMPANY button has been pressed",
        default=1,
    )

    vacancies = Column(
        BigInteger,
        nullable=False,
        comment="How much times the VACANCIES button has been pressed",
        default=1,
    )

    feedback = Column(
        Integer, nullable=False, comment="Feedback from student's", default=1
    )

    test = Column(
        Integer,
        nullable=False,
        comment="Test for human",
        default=1
    )

    def __repr__(self):
        return "<{0.__class__.__name__}(id={0.id!r})>".format(self)


class Department(BaseModel):
    __tablename__ = "department"

    department_name = Column(
        String, nullable=False, unique=True, comment="Programming language name"
    )

    customers = relationship("Customer", back_populates="department")
    courses = relationship("Course", back_populates="department")
    feedbacks = relationship("Feedback", back_populates="department")

    def __repr__(self):
        return self.department_name


class Customer(BaseModel):
    __tablename__ = "customer"

    chat_id = Column(
        Integer,
        nullable=False,
        comment="The chat id of User who applied for registration",
    )

    first_name = Column(
        String,
        nullable=False,
        comment="How much times the apply button has been pressed",
    )

    last_name = Column(
        String,
        nullable=True,
        comment="How much times the apply button has been pressed",
    )

    phone = Column(
        BigInteger,
        nullable=True,
        comment="How much times the apply button has been pressed",
    )

    time = Column(
        SmallInteger,
        nullable=True,
        comment="The time when a group start to study. Morning or Evening",
    )

    department_name = Column(
        String, ForeignKey("department.department_name"), nullable=False
    )

    department = relationship("Department", back_populates="customers")

    def __repr__(self):
        return f"{self.department_name} | {self.first_name} | {self.last_name}"


class User(BaseModel):
    __tablename__ = 'users'

    chat_id = Column(
        Integer,
        nullable=False,
        comment='chat_id'
    )

    username = Column(
        String,
        nullable=False,
        comment='Username'
    )

    first_name = Column(
        String,
        nullable=True,
        comment='First name'
    )

    last_name = Column(
        String,
        nullable=True,
        comment='Last name'
    )

    phone = Column(
        BigInteger,
        nullable=True,
        comment='Phone number'
    )

    current_page_on_vacancies = Column(
        Integer,
        nullable=False,
        comment='Current step',
        default=0
    )

    is_admin = Column(
        Boolean,
        nullable=False,
        comment='Is this user admin?',
        default=0
    )

    is_student = Column(
        Boolean,
        nullable=False,
        comment='Is this user admin?',
        default=0
    )

    def __repr__(self):
        return f'{self.first_name} | {self.last_name}'


class Course(BaseModel):
    __tablename__ = "course"

    department_id = Column(Integer, ForeignKey("department.id"), nullable=False)

    department = relationship("Department", back_populates="courses")

    department_info = Column(
        Text, nullable=False, comment="The information about course"
    )

    def __repr__(self):
        return f"{self.department}"


class Vacancy(BaseModel):
    __tablename__ = "vacancy"

    vacancy_type = Column(
        SmallInteger,
        nullable=False,
        comment="If VACANCY_TYPE = 0 it means that vacancy provided by P-Programist, otherwise the vacancy provided by another resource",
    )

    position = Column(String, nullable=False, comment="The header of vacancy")

    time = Column(String, nullable=False, comment="The time of lesson")

    salary = Column(String, nullable=False, comment="The salary of a mentor")

    details = Column(Text, nullable=False, comment="These are the details of vacancy")

    # This line is binded with the VACANCY field in VacancyApplicants class.
    applicants = relationship("VacancyApplicants", back_populates="vacancy")

    def __repr__(self):
        return self.position


class BishkekVacancy(BaseModel):
    """
    Эта модель создана специально для записи данных о вакансий по городу Бишкек
    с сайта "https://www.job.kg/" при помощи парсера "job_kg_parser.py".
    Она содержит поля:
    header -> Название вакансии
    company_name -> Название компании-работодателя
    required_experience -> Требуемый опыт работы
    salary -> Зарплата
    schedule -> Занятость в день
    details -> Подробное описание
    type -> Тип вакансии: Python/JavaScript/*еще что-то*...
    """

    __tablename__ = "bishkek_vacancy"

    header = Column(String, nullable=False, comment="The name of vacancy")

    company_name = Column(String, nullable=False, comment="The name of company")

    required_experience = Column(
        String, nullable=False, comment="Required work experience"
    )

    salary = Column(String, nullable=False, comment="The salary of a worker")

    schedule = Column(String, nullable=False, comment="The schedule of a work")

    details = Column(
        Text, nullable=False, comment="These are the description of vacancy"
    )

    link = Column(
        String,
        nullable=False,
        comment='The link of a vacancy'
    )

    type = Column(
        String,
        nullable=True,
        comment="These are the type of vacancy(Example: Python, JavaScript...)",
    )

    def __repr__(self):
        return self.header


class WorldVacancy(BaseModel):
    """
    Эта модель создана специально для записи данных о заказах со всего мира 
    с сайта "https://www.upwork.com/" при помощи парсера "upwork_parser.py".
    Она содержит поля:
    header -> Название вакансии
    description -> Подробное описание
    price -> Плата
    post_time -> Время подачи заказа
    tags -> Требуемые навыки
    type -> Тип вакансии: Python/JavaScript/*еще что-то*...
    link -> Ссылка на сам заказ
    """
    __tablename__ = 'world_vacancy'

    header = Column(
        String,
        nullable=False,
        comment='Заголовок проекта'
    )

    description = Column(
        Text,
        nullable=False,
        comment='Подробное описание проекта'
    )

    price = Column(
        String,
        nullable=False,
        comment='Плата за проект'
    )

    post_time = Column(
        String,
        nullable=False,
        comment='Время подачи проекта'
    )

    tags = Column(
        String,
        nullable=True,
        comment='Тэги проекта'
    )

    type = Column(
        String,
        nullable=True,
        comment='Тип проекта(Пример: Python, JavaScript...)'
    )

    link = Column(
        String,
        nullable=True,
        comment='Ссылка на оригинальный проект'
    )

    def __repr__(self):
        return self.header


class VacancyApplicants(BaseModel):
    __tablename__ = "vacancy_applicants"

    vacancy_id = Column(Integer, ForeignKey("vacancy.id"), nullable=False)

    vacancy = relationship("Vacancy", back_populates="applicants")

    chat_id = Column(
        Integer, nullable=False, comment="The chat id of User who applied for vacancy"
    )

    full_name = Column(String, nullable=True, comment="The full name of applicant")

    cover_letter = Column(
        Text,
        nullable=True,
        comment="This cover letter has to be written in order to see applicants's interests",
    )

    github_link = Column(
        String, nullable=True, comment="A GitHub link to check applicant's experience"
    )

    phone_number = Column(
        BigInteger, nullable=True, comment="The contact number of applicant"
    )

    def __repr__(self):
        return f"{self.full_name} - {self.phone_number}"


class Feedback(BaseModel):
    """
    Эта модель создана для записи отзывов, учеников курсов.
    Она содержит поля:
    telegram_id -> Телеграмм ID пользователя
    department_id -> Что обучает пользоваетль Python/JavaScript
    groups -> В какую смену обучается Утренняя/Вечерняя
    first_name -> Имя пользователя
    last_name -> Фамилия пользователя
    feedback_text -> Сам отзыв
    """
    __tablename__ = "feedback"

    telegram_id = Column(
        String, nullable=False, comment="Telegram ID of the person himself"
    )

    department_id = Column(
        Integer,
        ForeignKey("department.id"),
        nullable=False,
        comment="The group in which he is studying",
    )

    department = relationship("Department", back_populates="feedbacks")

    groups = Column(
        Integer, nullable=False, comment="Training time in the morning/evening - 0/1"
    )

    first_name = Column(
        String, nullable=True, comment="Student's first name", default="Empty"
    )

    last_name = Column(
        String, nullable=True, comment="Student's last name", default="Empty"
    )

    feedback_text = Column(
        String, comment="The student's review itself", nullable=False
    )

    def __repr__(self):
        return f"{self.department} - {self.first_name}"


class TestQuestions(BaseModel):
    """
    Эта модель создана для хранения вопросов.
    Она содержит поля:
    question -> Сам вопрос
    answers -> Варианты ответа
    true_answers -> Какой из них проваильный
    significance -> Сколько дает баллов тот или иной вопрос
    """
    __tablename__ = "test_questions"

    question = Column(VARCHAR(255), nullable=False, comment="The question itself")

    answers = Column(TEXT, nullable=False, comment="4 possible answers")

    true_answers = Column(
        String, nullable=False, comment="The field with the CORRECT answer"
    )

    significance = Column(Integer, comment="Significance of the issue", nullable=False)

    def __repr__(self):
        return f"{self.question} - {self.true_answers}"


if __name__ == "__main__":
    import asyncio
    from sqlalchemy.ext.asyncio import AsyncSession

    async def recreate_database():
        """
        When you want to set a connection with the database,
        You have to call the .begin() method from engine.
        After this method initialized You will get asynchronous connection with database.
        """
        async with engine.begin() as connection:
            await connection.run_sync(Base.metadata.drop_all)
            await connection.run_sync(Base.metadata.create_all)

        async with AsyncSession(engine, expire_on_commit=False) as session:
            async with session.begin():
                python = Department(id=1, department_name='Python')
                sys_admin = Department(
                    id=2, department_name='System Administrator')
                javascript = Department(id=3, department_name='Javascript')
                java = Department(id=4, department_name='Java')
                about = Reception(
                    apply=0, about_courses=0,
                    about_company=0, vacancies=0, feedback=0


                )
                session.add_all(
                    [about,
                        python,
                        sys_admin,
                        javascript,
                        java
                     ]
                )
                session.add_all([about, python, sys_admin, javascript, java])

            python_info = insert(Course).values(
                {"department_info": PYTHON_INFO_TEXT_RU, "department_id": python.id}
            )
            sys_admin_info = insert(Course).values(
                {
                    "department_info": SYS_ADMIN_INFO_TEXT_RU,
                    "department_id": sys_admin.id,
                }
            )
            javascript_info = insert(Course).values(
                {
                    "department_info": JAVASCRIPT_INFO_TEXT_RU,
                    "department_id": javascript.id,
                }
            )

            sys_admin_vacancy = insert(Vacancy).values(
                {
                    "vacancy_type": 0,
                    "position": "*М-Ментор на курс `Системный Администратор`*",
                    "time": "Договорный",
                    "salary": "*15000 - 25000 com*",
                    "details": """Требования:

    ✅ Чёткое понимание и возможность объяснить зачем нужна эта должность
    ✅ Опыт администрирования операционных систем Linux и Windows Server
    ✅ Английский - Pre-Intermediate | Intermediate
    ✅ Основы стека TCP/IP
    ✅ Умение использовать ActiveDirectory, DNS, DHCP
    ✅ Знание и понимание протоколов (FTP, SSH, SMTP, POP3, SAMBA)
    ✅ Знание любового скриптового ЯП
    ✅ Навыки работы с СУБД приветствуется
    ✅ Комерческий опыт работы от 1-2х лет



Обязанности:
    ⚜️ Разработка и поддержка учебного плана
    ⚜️ Обучение студентов, проведение занятий""",
                }
            )

            for question in QUESTIONS:
                questions = insert(TestQuestions).values(
                    {
                        "question": question[0],
                        "answers": question[1],
                        "true_answers": question[2],
                        "significance": question[3],
                    }
                )
                await session.execute(questions)

            await session.execute(python_info)
            await session.execute(sys_admin_info)
            await session.execute(javascript_info)
            await session.execute(sys_admin_vacancy)
            await session.commit()

    asyncio.run(recreate_database())
