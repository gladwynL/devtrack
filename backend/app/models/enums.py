import enum


class MembershipRole(enum.StrEnum):
    OWNER = "owner"
    MEMBER = "member"


class IssueStatus(enum.StrEnum):
    TODO = "todo"
    IN_PROGRESS = "in_progress"
    DONE = "done"


class IssuePriority(enum.StrEnum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"
