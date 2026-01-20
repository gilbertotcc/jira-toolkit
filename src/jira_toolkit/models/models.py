from __future__ import annotations

import dataclasses
from typing import TYPE_CHECKING, NewType


if TYPE_CHECKING:
    import datetime


IssueKey = NewType("IssueKey", str)


@dataclasses.dataclass(frozen=True)
class Board:
    id: int


@dataclasses.dataclass(frozen=True)
class Sprint:
    id: int
    name: str
    status: str
    start_date: datetime.datetime | None
    end_date: datetime.datetime | None
    issues: list[Issue] = dataclasses.field(default_factory=list)


@dataclasses.dataclass(frozen=True)
class Person:
    id: str
    name: str
    email_address: str | None


@dataclasses.dataclass(frozen=True)
class Status:
    id: str
    name: str


@dataclasses.dataclass(frozen=True)
class Issue:
    key: IssueKey
    summary: str
    status: Status
    issue_type: str
    assignee: Person | None
    reporter: Person | None
    story_points: float | None
