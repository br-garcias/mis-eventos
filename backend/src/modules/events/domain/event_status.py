from enum import StrEnum


class EventStatus(StrEnum):
    """Allowed transitions:
        DRAFT      → PUBLISHED, CANCELLED
        PUBLISHED  → ONGOING,   CANCELLED
        ONGOING    → FINISHED,  CANCELLED
        FINISHED   → (terminal)
        CANCELLED  → (terminal)
    """

    DRAFT = "draft"
    PUBLISHED = "published"
    ONGOING = "ongoing"
    FINISHED = "finished"
    CANCELLED = "cancelled"
