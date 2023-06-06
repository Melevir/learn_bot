import dataclasses
import datetime
import os
from typing import Iterable, cast

import pytest
from pytest_mock import MockerFixture
from sqlalchemy import Engine
from sqlalchemy.orm import Session
from telebot.types import Chat, Message, User as TelebotUser

from learn_bot.bot import Bot, compose_bot
from learn_bot.config import BotConfig
from learn_bot.db import Assignment, AssignmentStatusHistory, Course, Curator, Enrollment, Group, Student
from learn_bot.db.changers import create, delete_all_records_from
from learn_bot.db.enums import AssignmentStatus
from learn_bot.screenplay.db.changers import update_active_act_for
from learn_bot.screenplay.db.fetchers import fetch_user_by_chat_id
from learn_bot.screenplay.db.models.message import ChatMessage
from learn_bot.screenplay.db.models.screenplay_context import ScreenplayContext
from learn_bot.screenplay.db.models.user import User
from learn_bot.screenplay.services.play_act import play_active_act_for


@dataclasses.dataclass(frozen=True, kw_only=True, slots=True)
class ScreenplayTestPlayer:
    student: Student
    config: BotConfig
    user: User
    bot: Bot

    def play(self, play_name: str, user_phrases: list[str]) -> None:
        screenplay = self.bot.screenplay_director.get_play_by_name(play_name)
        assert screenplay
        with self.bot.get_session() as session:
            update_active_act_for(self.user.id, screenplay.name, screenplay.acts[0][0], session)

        for user_phrase in [f"/{screenplay.command_to_start}"] + user_phrases:
            message = self._compose_telegram_message_from_text(user_phrase)
            play_active_act_for(self.user, message, self.bot, self.config)

        with self.bot.get_session() as session:
            user = fetch_user_by_chat_id(self.user.telegram_chat_id, session)
        assert user
        assert user.active_screenplay_id is None
        assert user.active_act_id is None

    def _compose_telegram_message_from_text(self, user_phrase: str) -> Message:
        return Message(
            message_id=111111,
            from_user=TelebotUser(
                id=333333,
                is_bot=False,
                first_name=self.user.first_name,
            ),
            date=222222,
            chat=Chat(
                id=444444,
                type="private",
            ),
            content_type="text",
            options={"text": user_phrase},
            json_string="",
        )


@pytest.fixture
def config() -> BotConfig:
    return BotConfig(
        telegram_token="123",
        db_dsn=os.environ["TEST_DATABASE_DSN"],
    )


@pytest.fixture
def bot(config: BotConfig) -> Bot:
    return compose_bot(config)


@pytest.fixture
def db_engine(bot: Bot) -> Engine:
    return bot.db_engine


@pytest.fixture
def db_session(bot: Bot) -> Iterable[Session]:
    models = [
        AssignmentStatusHistory,
        Assignment,
        ChatMessage,
        ScreenplayContext,
        Student,
        Group,
        Curator,
        User,
        Enrollment,
        Course,
    ]

    with bot.get_session() as session:
        for model in models:
            delete_all_records_from(model, session)

        yield session

        for model in models:
            delete_all_records_from(model, session)


@pytest.fixture
def correct_assignment_url() -> str:
    return "https://github.com/Melevir/learn_bot"


@pytest.fixture
def student_player(
    student: Student,
    config: BotConfig,
    user: User,
    bot: Bot,
    mocker: MockerFixture,
) -> ScreenplayTestPlayer:
    mocker.patch("learn_bot.bot.Bot.send_message")
    return ScreenplayTestPlayer(student=student, config=config, user=user, bot=bot)


@pytest.fixture
def student(db_session: Session, group: Group) -> Student:
    return cast(Student, create(
        Student(
            first_name="John",
            last_name="Doe",
            telegram_nickname="john",
            telegram_chat_id="444444",
            group_id=group.id,
        ),
        db_session,
    ))


@pytest.fixture
def group(db_session: Session, enrollment: Enrollment, curator: Curator) -> Group:
    return cast(Group, create(
        Group(
            telegram_chat_id="777777",
            enrollment_id=enrollment.id,
            curator_id=curator.id,
        ),
        db_session,
    ))


@pytest.fixture
def enrollment(db_session: Session, course: Course) -> Enrollment:
    return cast(Enrollment, create(
        Enrollment(
            number=1,
            date_start=datetime.date(2023, 1, 1),
            date_end=datetime.date(2123, 1, 1),
            course_id=course.id,
        ),
        db_session,
    ))


@pytest.fixture
def curator(db_session: Session) -> Curator:
    return cast(Curator, create(
        Curator(
            first_name="John",
            last_name="Doe",
            telegram_nickname="john",
            telegram_chat_id="444444",
        ),
        db_session,
    ))


@pytest.fixture
def course(db_session: Session) -> Course:
    return cast(Course, create(
        Course(
            title="Course",
        ),
        db_session,
    ))


@pytest.fixture
def user(db_session: Session) -> User:
    return cast(User, create(
        User(
            first_name="John",
            last_name="Doe",
            telegram_nickname="john",
            telegram_chat_id="444444",
        ),
        db_session,
    ))


@pytest.fixture
def pending_assignment(db_session: Session, correct_assignment_url: str, student: Student) -> Assignment:
    return cast(Assignment, create(
        Assignment(
            url=correct_assignment_url,
            status=AssignmentStatus.READY_FOR_REVIEW,
            student_id=student.id,
        ),
        db_session,
    ))
