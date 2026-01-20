from __future__ import annotations

import dataclasses
import os
from typing import TYPE_CHECKING, Any, TypeVar

from dotenv import load_dotenv
from jira import JIRA, Issue

from ..infrastructure.mappings import board_from_raw_board, sprint_from_raw_sprint_and_issues


if TYPE_CHECKING:
    from collections.abc import Callable

    from ..models import Board, Sprint


T = TypeVar("T") # Define a TypeVar for the elements in the paginated list


# Jira Custom Field IDs
# customfield_10026 typically represents "Story Points" in Jira instances
JIRA_CUSTOM_FIELD_STORY_POINTS = "customfield_10026"
# customfield_10020 represents the "Sprint" field, containing sprint details for an issue
JIRA_CUSTOM_FIELD_SPRINT_INFO = "customfield_10020"

# Fields to retrieve when searching for Jira issues
JIRA_ISSUE_SEARCH_FIELDS = [
    "key",
    "summary",
    "status",
    "issuetype",
    "assignee",
    "reporter",
    JIRA_CUSTOM_FIELD_STORY_POINTS,
    JIRA_CUSTOM_FIELD_SPRINT_INFO,
]


def _get_all_startat_paginated_results[T](
    func: Callable[..., list[T]],
    *args: Any,
    **kwargs: Any,
) -> list[T]:
    """
    JIRA paginated results return a list of items. This function helps to retrieve all of them.
    The `maxResults` and `startAt` arguments are used to control pagination.
    """
    results: list[T] = []
    start_at = 0
    page_size = 50

    while True:
        page = func(
            *args,
            **kwargs,
            startAt=start_at,
            maxResults=page_size,
        )
        results.extend(page)

        if len(page) < page_size:
            break
        start_at += page_size

    return results


def _get_all_token_paginated_results[T](
    func: Callable[..., Any], # This is tricky as 'page' is an iterable, not necessarily a list, and has an attribute
    **kwargs: Any,
) -> list[T]:
    """
    JIRA paginated results that use nextPageToken.
    It is assumed that the function returns an object that can be iterated over
    and has a `nextPageToken` attribute.
    """
    results: list[T] = []
    token = None
    while True:
        page = func(nextPageToken=token, **kwargs)
        results.extend(page)

        next_token = getattr(page, "nextPageToken", None)
        if not next_token:
            break
        token = next_token

    return results


@dataclasses.dataclass(frozen=True)
class JiraConfig:
    server_url: str
    user: str
    token: str

    @classmethod
    def load(cls) -> JiraConfig:
        load_dotenv()

        server_url = os.getenv("JIRA_SERVER")
        user = os.getenv("JIRA_USER")
        token = os.getenv("JIRA_TOKEN")

        if not (server_url and user and token):
            raise RuntimeError("Environment variables JIRA_USER and JIRA_TOKEN must be set")

        return cls(server_url, user, token)


@dataclasses.dataclass(frozen=True)
class JiraClient:
    client: JIRA

    @classmethod
    def get_instance(cls, configuration: JiraConfig | None = None) -> JiraClient:
        jira_config = configuration or JiraConfig.load()
        jira_client = JIRA(
            server=jira_config.server_url,
            basic_auth=(jira_config.user, jira_config.token),
        )
        return cls(jira_client)

    def find_scrum_boards_by_project_key(self, project_key: str) -> list[Board]:
        raw_boards = _get_all_startat_paginated_results(
            self.client.boards,
            projectKeyOrID=project_key,
            type="scrum",
        )
        return [board_from_raw_board(raw_board) for raw_board in raw_boards]


    def get_open_sprints_by_board(self, board: Board) -> list[Sprint]:
        raw_sprints = _get_all_startat_paginated_results(self.client.sprints, board_id=board.id, state="active")

        if not raw_sprints:
            return []

        sprint_ids = [s.id for s in raw_sprints]
        jql = f"sprint IN ({','.join(map(str, sprint_ids))})"

        all_raw_issues: list[Issue] = _get_all_token_paginated_results(
            self.client.enhanced_search_issues,
            jql_str=jql,
            fields=",".join(JIRA_ISSUE_SEARCH_FIELDS),
        )

        issues_by_sprint_id: dict[int, list[Issue]] = {sprint_id: [] for sprint_id in sprint_ids}
        for issue in all_raw_issues:
            for sprint_info in getattr(issue.fields, JIRA_CUSTOM_FIELD_SPRINT_INFO, []):
                sprint_id = int(sprint_info.id)
                if sprint_id in issues_by_sprint_id:
                    issues_by_sprint_id[sprint_id].append(issue)

        sprints: list[Sprint] = []
        for raw_sprint in raw_sprints:
            issues_for_sprint = issues_by_sprint_id.get(raw_sprint.id, [])
            sprint = sprint_from_raw_sprint_and_issues(raw_sprint, issues_for_sprint)
            sprints.append(sprint)

        return sprints
