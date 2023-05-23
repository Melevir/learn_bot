from enum import Enum


class AssignmentStatus(Enum):
    READY_FOR_REVIEW = "READY_FOR_REVIEW"
    REVIEW_IN_PROGRESS = "REVIEW_IN_PROGRESS"
    REVIEWED = "REVIEWED"

    @classmethod
    def get_pending_for_student_statuses(cls) -> set["AssignmentStatus"]:
        return {cls.READY_FOR_REVIEW, cls.REVIEW_IN_PROGRESS}
