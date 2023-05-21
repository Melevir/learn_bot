from sqlalchemy.orm import Session

from learn_bot.db import Student
from learn_bot.db.enums import AssignmentStatus
from learn_bot.db.fetchers import fetch_all_assignments_for_student
from learn_bot.tests.conftest import ScreenplayTestPlayer


def test__submit_assignment__success_case(
    correct_assignment_url: str,
    student_player: ScreenplayTestPlayer,
    student: Student,
    db_session: Session,
) -> None:
    student_player.play(
        play_name="student.submit_assignment",
        user_phrases=[
            correct_assignment_url,
            "Нет, пока хватит",
        ],
    )
    assignments = fetch_all_assignments_for_student(student, db_session)

    assert len(assignments) == 1
    assert assignments[0].url == correct_assignment_url
    assert assignments[0].status == AssignmentStatus.READY_FOR_REVIEW
