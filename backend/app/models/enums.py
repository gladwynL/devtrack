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


class IssueActivityEventType(enum.StrEnum):
    CREATED = "created"
    TITLE_CHANGED = "title_changed"
    DESCRIPTION_CHANGED = "description_changed"
    STATUS_CHANGED = "status_changed"
    PRIORITY_CHANGED = "priority_changed"
    ASSIGNEE_CHANGED = "assignee_changed"
