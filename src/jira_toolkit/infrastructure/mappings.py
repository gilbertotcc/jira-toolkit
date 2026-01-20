from datetime import datetime
from typing import Any

from ..models import Board, Issue, IssueKey, Person, Sprint, Status


def board_from_raw_board(raw_board: Any) -> Board:
    return Board(raw_board.id)


def sprint_from_raw_sprint_and_issues(raw_sprint: Any, raw_issues: list[Any]) -> Sprint:
    start_date = None if not raw_sprint.startDate else datetime.fromisoformat(raw_sprint.startDate)
    end_date = None if not raw_sprint.endDate else datetime.fromisoformat(raw_sprint.endDate)

    issues = [issue_from_raw_issue(raw_issue) for raw_issue in raw_issues]

    return Sprint(
        id=raw_sprint.id,
        name=raw_sprint.name,
        status=raw_sprint.state,
        start_date=start_date,
        end_date=end_date,
        issues=issues
    )


def person_from_raw_user(raw_user: Any) -> Person:
    return Person(
        id=raw_user.accountId,
        name=raw_user.displayName,
        email_address=getattr(raw_user, "emailAddress", None),
    )


def status_from_raw_status(raw_status: Any) -> Status:
    return Status(id=raw_status.id, name=raw_status.name)


def issue_from_raw_issue(raw_issue: Any) -> Issue:
    story_points = getattr(raw_issue.fields, "customfield_10026", None)
    return Issue(
        key=IssueKey(raw_issue.key),
        summary=raw_issue.fields.summary,
        status=status_from_raw_status(raw_issue.fields.status),
        issue_type=raw_issue.fields.issuetype.name,
        assignee=person_from_raw_user(raw_issue.fields.assignee) if raw_issue.fields.assignee else None,
        reporter=person_from_raw_user(raw_issue.fields.reporter) if raw_issue.fields.reporter else None,
        story_points=float(story_points) if story_points is not None else None,
    )
