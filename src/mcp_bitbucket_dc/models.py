"""Pydantic models for Bitbucket Data Center API responses."""

from __future__ import annotations

from typing import Any, Optional

from pydantic import BaseModel, Field

# ── Pagination ──────────────────────────────────────────────────────────────


class PagedResponse(BaseModel):
    """Generic paginated response wrapper from Bitbucket DC REST API."""

    size: int = 0
    limit: int = 25
    start: int = 0
    is_last_page: bool = Field(True, alias="isLastPage")
    next_page_start: Optional[int] = Field(None, alias="nextPageStart")
    values: list[dict[str, Any]] = []


# ── Projects ────────────────────────────────────────────────────────────────


class Project(BaseModel):
    key: str
    id: int
    name: str
    public: Optional[bool] = None
    type: str = ""
    description: Optional[str] = None


# ── Repositories ────────────────────────────────────────────────────────────


class Repository(BaseModel):
    slug: str
    id: int
    name: str
    scm_id: str = Field("git", alias="scmId")
    state: str = ""
    status_message: str = Field("", alias="statusMessage")
    forkable: bool = True
    project: Optional[Project] = None
    public: bool = False
    archived: bool = False
    description: Optional[str] = None


# ── Branches & Tags ────────────────────────────────────────────────────────


class Ref(BaseModel):
    """Branch or tag reference."""

    id: str
    display_id: str = Field("", alias="displayId")
    type: str = ""
    latest_commit: Optional[str] = Field(None, alias="latestCommit")
    is_default: bool = Field(False, alias="isDefault")


# ── Commits ─────────────────────────────────────────────────────────────────


class CommitAuthor(BaseModel):
    name: str = ""
    email_address: str = Field("", alias="emailAddress")


class Commit(BaseModel):
    id: str
    display_id: str = Field("", alias="displayId")
    message: str = ""
    author: Optional[CommitAuthor] = None
    author_timestamp: Optional[int] = Field(None, alias="authorTimestamp")
    parents: list[dict[str, Any]] = []


# ── Pull Requests ───────────────────────────────────────────────────────────


class PullRequestRef(BaseModel):
    id: str
    display_id: str = Field("", alias="displayId")
    latest_commit: Optional[str] = Field(None, alias="latestCommit")
    repository: Optional[Repository] = None


class PullRequestUser(BaseModel):
    name: str = ""
    display_name: str = Field("", alias="displayName")
    email_address: Optional[str] = Field(None, alias="emailAddress")
    slug: Optional[str] = None


class PullRequestParticipant(BaseModel):
    user: PullRequestUser
    role: str = ""
    approved: bool = False
    status: str = ""


class PullRequest(BaseModel):
    id: int
    title: str = ""
    description: Optional[str] = None
    state: str = ""
    created_date: Optional[int] = Field(None, alias="createdDate")
    updated_date: Optional[int] = Field(None, alias="updatedDate")
    from_ref: Optional[PullRequestRef] = Field(None, alias="fromRef")
    to_ref: Optional[PullRequestRef] = Field(None, alias="toRef")
    author: Optional[PullRequestParticipant] = None
    reviewers: list[PullRequestParticipant] = []
    locked: bool = False


# ── PR Changes / Diff ──────────────────────────────────────────────────────


class PathInfo(BaseModel):
    """File path information in a PR change."""

    components: list[str] = []
    name: str = ""
    to_string: str = Field("", alias="toString")


class PullRequestChange(BaseModel):
    content_id: str = Field("", alias="contentId")
    from_content_id: str = Field("", alias="fromContentId")
    path: Optional[PathInfo] = None
    src_path: Optional[PathInfo] = Field(None, alias="srcPath")
    type: str = ""
    node_type: str = Field("", alias="nodeType")


# ── PR Comments / Activities ───────────────────────────────────────────────


class CommentAnchor(BaseModel):
    path: Optional[str] = None
    line: Optional[int] = None
    line_type: Optional[str] = Field(None, alias="lineType")
    file_type: Optional[str] = Field(None, alias="fileType")


class Comment(BaseModel):
    id: int
    text: str = ""
    author: Optional[PullRequestUser] = None
    created_date: Optional[int] = Field(None, alias="createdDate")
    updated_date: Optional[int] = Field(None, alias="updatedDate")
    severity: str = ""
    state: str = ""
    anchor: Optional[CommentAnchor] = None
    comments: list[Comment] = []


# Self-referencing model needs update_forward_refs
Comment.model_rebuild()


class Activity(BaseModel):
    id: int
    action: str = ""
    comment: Optional[Comment] = None
    user: Optional[PullRequestUser] = None
    created_date: Optional[int] = Field(None, alias="createdDate")


# ── File Browsing ───────────────────────────────────────────────────────────


class FileNode(BaseModel):
    """A file or directory entry from the browse endpoint."""

    path: Optional[PathInfo] = None
    content_id: Optional[str] = Field(None, alias="contentId")
    type: str = ""  # "FILE" or "DIRECTORY"
    size: Optional[int] = None


class BrowseResponse(BaseModel):
    """Response from the browse endpoint."""

    path: Optional[PathInfo] = None
    children: Optional[PagedResponse] = None
    # For file content
    lines: Optional[list[dict[str, Any]]] = None
    size: Optional[int] = None


# ── Code Search ─────────────────────────────────────────────────────────────


class HitContext(BaseModel):
    line: int
    text: str


class PathMatch(BaseModel):
    text: str
    match: Optional[bool] = None


class SearchResult(BaseModel):
    repository: Repository
    file: str
    hit_contexts: list[list[HitContext]] = Field([], alias="hitContexts")
    path_matches: list[PathMatch] = Field([], alias="pathMatches")
    hit_count: int = Field(0, alias="hitCount")


class CodeSection(BaseModel):
    category: str = ""
    is_last_page: bool = Field(True, alias="isLastPage")
    count: int = 0
    start: int = 0
    next_start: int = Field(0, alias="nextStart")
    values: list[SearchResult] = []


class SearchScope(BaseModel):
    type: str = ""


class QueryInfo(BaseModel):
    substituted: bool = False


class BitbucketSearchResponse(BaseModel):
    scope: Optional[SearchScope] = None
    code: Optional[CodeSection] = None
    query: Optional[QueryInfo] = None
