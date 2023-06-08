import datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from learn_bot.db import Assignment, Course, Curator, Enrollment, Group, Student
from learn_bot.db.enums import AssignmentStatus, UserRole
from learn_bot.screenplay.db.models.user import User


def fetch_courses(session: Session) -> list[Course]:
    return list(session.scalars(
        select(Course),
    ).all())


def fetch_curator_by_chat_id(chat_id: str | None, session: Session) -> Curator | None:
    if chat_id is None:
        return None
    return session.scalar(
        select(Curator).where(
            Curator.telegram_chat_id == chat_id,
        ),
    )


def fetch_curator_by_telegram_nickname(nickname: str | None, session: Session) -> Curator | None:
    if nickname is None:
        return None
    return session.scalar(
        select(Curator).where(
            Curator.telegram_nickname == nickname.lower(),
        ),
    )


def fetch_student_by_id(student_id: int, session: Session) -> Student | None:
    return session.scalar(
        select(Student).where(
            Student.id == student_id,
        ),
    )


def fetch_student_by_chat_id(chat_id: str | None, session: Session) -> Student | None:
    if chat_id is None:
        return None
    return session.scalar(
        select(Student).where(
            Student.telegram_chat_id == str(chat_id),
        ),
    )


def fetch_student_by_telegram_nickname(nickname: str | None, session: Session) -> Student | None:
    if nickname is None:
        return None
    return session.scalar(
        select(Student).where(
            Student.telegram_nickname == nickname.lower(),
        ),
    )


def fetch_not_connected_student_by_auth_code(auth_code: str, session: Session) -> Student | None:
    return session.scalar(
        select(Student).where(
            Student.auth_code == auth_code,
            Student.telegram_chat_id.is_(None),
        ),
    )


def fetch_assignments_for_curator(
    curator_id: int,
    statuses: list[AssignmentStatus],
    session: Session,
) -> list[Assignment]:
    return list(session.scalars(
        select(Assignment).join(Student).join(Group).filter(
            Assignment.status.in_(statuses),
            Group.curator_id == curator_id,
        ).order_by(Assignment.created_at),
    ).all())


def fetch_oldest_pending_assignment_for_curator(curator_id: int, session: Session) -> Assignment | None:
    return session.scalar(
        select(Assignment).join(Student).join(Group).filter(
            Assignment.status == AssignmentStatus.READY_FOR_REVIEW,
            Group.curator_id == curator_id,
        ).order_by(Assignment.created_at).limit(1),
    )


def fetch_assignment_by_id(assignment_id: int, session: Session) -> Assignment | None:
    return session.scalar(
        select(Assignment).where(
            Assignment.id == assignment_id,
        ),
    )


def fetch_role_by_user(user: User, session: Session) -> UserRole:
    curator = fetch_curator_by_telegram_nickname(user.telegram_nickname, session)
    student = (
        fetch_student_by_telegram_nickname(user.telegram_nickname, session)
        or fetch_student_by_chat_id(user.telegram_chat_id, session)
    )
    return (
        UserRole.CURATOR
        if curator is not None
        else UserRole.STUDENT if student is not None else UserRole.ANONYMOUS
    )


def fetch_active_groups_for_curator(curator: Curator, session: Session) -> list[Group]:
    return list(session.scalars(
        select(Group).join(Enrollment).filter(
            Group.curator_id == curator.id,
            Enrollment.date_end >= datetime.date.today(),
        ).order_by(Group.created_at),
    ).all())


def fetch_students_in_group(group: Group, session: Session) -> list[Student]:
    return list(session.scalars(
        select(Student).filter(
            Student.group_id == group.id,
        ).order_by(Student.created_at),
    ).all())


def fetch_all_assignments_for_student(student: Student, session: Session) -> list[Assignment]:
    return list(session.scalars(
        select(Assignment).filter(
            Assignment.student_id == student.id,
        ).order_by(Assignment.created_at),
    ).all())


def fetch_all_assignments_for_student_in_period(
    student: Student,
    date_from: datetime.date,
    date_to: datetime.date,
    session: Session,
) -> list[Assignment]:
    return list(session.scalars(
        select(Assignment).filter(
            Assignment.student_id == student.id,
            Assignment.created_at >= date_from,
            Assignment.created_at <= date_to,
        ).order_by(Assignment.created_at),
    ).all())


def fetch_assignments_by_url(
    assignment_url: str,
    student_id: int,
    statuses: set[AssignmentStatus],
    session: Session,
) -> list[Assignment]:
    return list(session.scalars(
        select(Assignment).filter(
            Assignment.student_id == student_id,
            Assignment.url == assignment_url,
            Assignment.status.in_(statuses),
        ).order_by(Assignment.created_at),
    ).all())


def find_similar_curator(curator: Curator, session: Session) -> Curator | None:
    return session.scalar(
        select(Curator).where(
            Curator.first_name == curator.first_name,
            Curator.last_name == curator.last_name,
        ),
    )


def find_similar_course(course: Course, session: Session) -> Course | None:
    return session.scalar(
        select(Course).where(
            Course.title == course.title,
        ),
    )


def find_similar_enrollment(enrollment: Enrollment, session: Session) -> Enrollment | None:
    return session.scalar(
        select(Enrollment).where(
            Enrollment.course_id == enrollment.course_id,
            Enrollment.number == enrollment.number,
            Enrollment.date_start == enrollment.date_start,
            Enrollment.date_end == enrollment.date_end,
        ),
    )


def find_similar_group(group: Group, session: Session) -> Group | None:
    return session.scalar(
        select(Group).where(
            Group.enrollment_id == group.enrollment_id,
            Group.curator_id == group.curator_id,
        ),
    )


def find_similar_student(student: Student, session: Session) -> Student | None:  # noqa: CFQ004
    same_auth_code_student = session.scalar(
        select(Student).where(
            Student.auth_code == student.auth_code,
        ),
    ) if student.auth_code else None
    if same_auth_code_student:
        return same_auth_code_student

    same_tg_nickname_student = session.scalar(
        select(Student).where(
            Student.telegram_nickname == student.telegram_nickname,
        ),
    ) if student.telegram_nickname else None
    if same_tg_nickname_student:
        return same_tg_nickname_student

    same_email_student = session.scalar(
        select(Student).where(
            Student.email == student.email,
        ),
    ) if student.email else None
    if same_email_student:
        return same_email_student

    same_timepad_id_student = session.scalar(
        select(Student).where(
            Student.timepad_id == student.timepad_id,
        ),
    ) if student.timepad_id else None
    if same_timepad_id_student:
        return same_timepad_id_student

    return None
