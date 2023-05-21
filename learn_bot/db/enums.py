from enum import Enum


class AssignmentStatus(Enum):
    READY_FOR_REVIEW = "READY_FOR_REVIEW"
    REVIEW_IN_PROGRESS = "REVIEW_IN_PROGRESS"
    REVIEWED = "REVIEWED"
