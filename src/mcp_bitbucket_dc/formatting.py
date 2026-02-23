"""Markdown formatting helpers for Bitbucket API responses."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Any, Optional


def _ts(epoch_ms: Optional[int]) -> str:
    """Convert epoch milliseconds to readable date string."""
    if epoch_ms is None:
        return "unknown"
    dt = datetime.fromtimestamp(epoch_ms / 1000, tz=timezone.utc)
    return dt.strftime("%Y-%m-%d %H:%M UTC")


def render_response(response_format: str, markdown: str, data: Any) -> str:
    """Return markdown or JSON output depending on the requested format."""
    if response_format == "json":
        return json.dumps(data, indent=2, ensure_ascii=False)
    return markdown


# ── Projects & Repos ────────────────────────────────────────────────────────


def format_project(p: dict[str, Any]) -> str:
    desc = p.get("description", "") or ""
    public = "Public" if p.get("public") else "Private"
    return (
        f"- **{p.get('name', '')}** (`{p.get('key', '')}`) — {public}{f' — {desc}' if desc else ''}"
    )


def format_projects(projects: list[dict[str, Any]], total: int, is_last: bool) -> str:
    lines = [f"# Projects ({total} total)\n"]
    lines.extend(format_project(p) for p in projects)
    if not is_last:
        lines.append("\n*More projects available — increase `start` to paginate.*")
    return "\n".join(lines)


def format_repository(r: dict[str, Any]) -> str:
    state = r.get("state", "")
    archived = " [ARCHIVED]" if r.get("archived") else ""
    desc = r.get("description", "") or ""
    project_key = r.get("project", {}).get("key", "")
    return (
        f"- **{r.get('name', '')}** (`{r.get('slug', '')}`) "
        f"in `{project_key}` — {state}{archived}"
        f"{f' — {desc}' if desc else ''}"
    )


def format_repositories(repos: list[dict[str, Any]], total: int, is_last: bool) -> str:
    lines = [f"# Repositories ({total} total)\n"]
    lines.extend(format_repository(r) for r in repos)
    if not is_last:
        lines.append("\n*More repositories available — increase `start` to paginate.*")
    return "\n".join(lines)


def format_repository_detail(r: dict[str, Any]) -> str:
    project = r.get("project", {})
    links = r.get("links", {})
    clone_urls = links.get("clone", [])
    clone_section = ""
    if clone_urls:
        clone_section = "\n**Clone URLs:**\n" + "\n".join(
            f"  - {c.get('name', '')}: `{c.get('href', '')}`" for c in clone_urls
        )
    return (
        f"# {r.get('name', '')}\n\n"
        f"- **Slug:** `{r.get('slug', '')}`\n"
        f"- **Project:** {project.get('name', '')} (`{project.get('key', '')}`)\n"
        f"- **State:** {r.get('state', '')}\n"
        f"- **SCM:** {r.get('scmId', 'git')}\n"
        f"- **Forkable:** {r.get('forkable', True)}\n"
        f"- **Public:** {r.get('public', False)}\n"
        f"- **Archived:** {r.get('archived', False)}\n"
        f"- **Description:** {r.get('description', '') or 'N/A'}"
        f"{clone_section}"
    )


# ── Branches & Tags ────────────────────────────────────────────────────────


def format_branches(branches: list[dict[str, Any]], total: int, is_last: bool) -> str:
    lines = [f"# Branches ({total} total)\n"]
    for b in branches:
        default = " ⭐ **default**" if b.get("isDefault") else ""
        lines.append(
            f"- `{b.get('displayId', '')}` — latest commit: "
            f"`{(b.get('latestCommit', '') or '')[:12]}`{default}"
        )
    if not is_last:
        lines.append("\n*More branches available — increase `start` to paginate.*")
    return "\n".join(lines)


def format_tags(tags: list[dict[str, Any]], total: int, is_last: bool) -> str:
    lines = [f"# Tags ({total} total)\n"]
    for t in tags:
        lines.append(
            f"- `{t.get('displayId', '')}` — commit: `{(t.get('latestCommit', '') or '')[:12]}`"
        )
    if not is_last:
        lines.append("\n*More tags available — increase `start` to paginate.*")
    return "\n".join(lines)


# ── Commits ─────────────────────────────────────────────────────────────────


def format_commit(c: dict[str, Any]) -> str:
    author = c.get("author", {})
    name = author.get("name", "unknown")
    msg = (c.get("message", "") or "").split("\n")[0]  # first line only
    ts = _ts(c.get("authorTimestamp"))
    return f"- `{(c.get('displayId', '') or c.get('id', ''))[:12]}` {ts} **{name}** — {msg}"


def format_commits(commits: list[dict[str, Any]], total: int, is_last: bool) -> str:
    lines = [f"# Commits ({total} total)\n"]
    lines.extend(format_commit(c) for c in commits)
    if not is_last:
        lines.append("\n*More commits available — increase `start` to paginate.*")
    return "\n".join(lines)


# ── Pull Requests ───────────────────────────────────────────────────────────


def format_pr_summary(pr: dict[str, Any]) -> str:
    author = pr.get("author", {}).get("user", {})
    author_name = author.get("displayName", author.get("name", "unknown"))
    state = pr.get("state", "")
    from_ref = pr.get("fromRef", {}).get("displayId", "?")
    to_ref = pr.get("toRef", {}).get("displayId", "?")
    return (
        f"- **#{pr.get('id', '')}** [{state}] {pr.get('title', '')} "
        f"(`{from_ref}` → `{to_ref}`) by {author_name} — {_ts(pr.get('updatedDate'))}"
    )


def format_pull_requests(prs: list[dict[str, Any]], total: int, is_last: bool) -> str:
    lines = [f"# Pull Requests ({total} total)\n"]
    lines.extend(format_pr_summary(pr) for pr in prs)
    if not is_last:
        lines.append("\n*More pull requests available — increase `start` to paginate.*")
    return "\n".join(lines)


def format_pull_request_detail(pr: dict[str, Any]) -> str:
    author = pr.get("author", {}).get("user", {})
    author_name = author.get("displayName", author.get("name", "unknown"))
    from_ref = pr.get("fromRef", {})
    to_ref = pr.get("toRef", {})
    reviewers = pr.get("reviewers", [])

    reviewer_lines = []
    for r in reviewers:
        user = r.get("user", {})
        status = "✅ Approved" if r.get("approved") else f"({r.get('status', 'UNAPPROVED')})"
        reviewer_lines.append(f"  - {user.get('displayName', user.get('name', ''))} {status}")

    return (
        f"# PR #{pr.get('id', '')} — {pr.get('title', '')}\n\n"
        f"- **State:** {pr.get('state', '')}\n"
        f"- **Author:** {author_name}\n"
        f"- **Branch:** `{from_ref.get('displayId', '?')}` → `{to_ref.get('displayId', '?')}`\n"
        f"- **Created:** {_ts(pr.get('createdDate'))}\n"
        f"- **Updated:** {_ts(pr.get('updatedDate'))}\n"
        f"- **Locked:** {pr.get('locked', False)}\n\n"
        f"## Description\n\n{pr.get('description', '') or 'No description.'}\n\n"
        f"## Reviewers ({len(reviewers)})\n\n"
        + ("\n".join(reviewer_lines) if reviewer_lines else "No reviewers assigned.")
    )


def format_pr_changes(changes: list[dict[str, Any]], total: int, is_last: bool) -> str:
    lines = [f"# PR Changes ({total} files)\n"]
    for c in changes:
        path_info = c.get("path", {})
        file_path = path_info.get("toString", path_info.get("name", "?"))
        change_type = c.get("type", "?")
        node_type = c.get("nodeType", "")
        src = c.get("srcPath", {})
        rename = ""
        if src and src.get("toString"):
            rename = f" (was `{src['toString']}`)"
        lines.append(f"- **{change_type}** `{file_path}`{rename} [{node_type}]")
    if not is_last:
        lines.append("\n*More changes available — increase `start` to paginate.*")
    return "\n".join(lines)


def format_pr_activities(activities: list[dict[str, Any]], total: int, is_last: bool) -> str:
    lines = [f"# PR Activity ({total} items)\n"]
    for a in activities:
        action = a.get("action", "")
        user = a.get("user", {})
        user_name = user.get("displayName", user.get("name", "unknown"))
        ts = _ts(a.get("createdDate"))

        comment = a.get("comment")
        if comment:
            text = (comment.get("text", "") or "")[:200]
            anchor = comment.get("anchor")
            location = ""
            if anchor and anchor.get("path"):
                location = f" on `{anchor['path']}`"
                if anchor.get("line"):
                    location += f" line {anchor['line']}"
            lines.append(f"### {action} by {user_name} — {ts}{location}\n\n{text}\n")
        else:
            lines.append(f"- **{action}** by {user_name} — {ts}")

    if not is_last:
        lines.append("\n*More activities available — increase `start` to paginate.*")
    return "\n".join(lines)


# ── File Browsing ───────────────────────────────────────────────────────────


def format_browse(data: dict[str, Any], path: str) -> str:
    """Format the browse API response (directory listing or file content)."""
    children = data.get("children")
    if children:
        # Directory listing
        values = children.get("values", [])
        total = children.get("size", len(values))
        is_last = children.get("isLastPage", True)
        display_path = path or "/"
        lines = [f"# Browse: `{display_path}` ({total} entries)\n"]
        for entry in values:
            entry_path = entry.get("path", {})
            name = entry_path.get("toString", entry_path.get("name", "?"))
            entry_type = entry.get("type", "")
            size = entry.get("size")
            if entry_type == "DIRECTORY":
                lines.append(f"- 📁 `{name}/`")
            else:
                size_str = f" ({_format_size(size)})" if size is not None else ""
                lines.append(f"- 📄 `{name}`{size_str}")
        if not is_last:
            lines.append("\n*More entries available — increase `start` to paginate.*")
        return "\n".join(lines)

    # File content
    file_lines = data.get("lines", [])
    if file_lines:
        content_lines = [f"# File: `{path}`\n\n```"]
        for line_obj in file_lines:
            content_lines.append(line_obj.get("text", ""))
        content_lines.append("```")
        return "\n".join(content_lines)

    return f"# Browse: `{path}`\n\nEmpty or binary file."


def format_file_list(files: list[str], path: str, total: int, is_last: bool) -> str:
    display_path = path or "/"
    lines = [f"# Files in `{display_path}` ({total} total)\n"]
    lines.extend(f"- `{f}`" for f in files)
    if not is_last:
        lines.append("\n*More files available — increase `start` to paginate.*")
    return "\n".join(lines)


def _format_size(size_bytes: Optional[int]) -> str:
    if size_bytes is None:
        return ""
    if size_bytes < 1024:
        return f"{size_bytes} B"
    if size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.1f} KB"
    return f"{size_bytes / (1024 * 1024):.1f} MB"


# ── Code Search ─────────────────────────────────────────────────────────────


def format_search_results(
    results: list[dict[str, Any]],
    query: str,
    total: int,
    is_last: bool,
) -> str:
    """Format code search results as markdown."""
    more = "" if is_last else " | **More pages available**"
    header = (
        f'# Search Results for "{query}"\n\n'
        f"**Total Results:** {total} | **Showing:** {len(results)} results{more}\n\n---\n"
    )

    sections = []
    for i, result in enumerate(results, 1):
        repo = result.get("repository", {})
        project = repo.get("project", {})
        file_path = result.get("file", "?")
        hit_count = result.get("hitCount", 0)
        repo_name = repo.get("name", "")
        project_key = project.get("key", "")

        section = (
            f"## {i}. {file_path}\n"
            f"**Project:** {project_key} | **Repository:** {repo_name} | "
            f"**Matches:** {hit_count}\n\n"
        )

        hit_contexts = result.get("hitContexts", [])
        blocks = _extract_context_blocks(hit_contexts)
        for j, block in enumerate(blocks):
            if j > 0:
                section += "---\n\n"
            section += "```\n"
            for ctx in block:
                text = _clean_html(ctx.get("text", ""))
                section += f"{ctx.get('line', 0):4d}    {text}\n"
            section += "```\n\n"

        sections.append(section)

    return header + "\n---\n\n".join(sections) + "\n---\n\n*Search completed*"


def _extract_context_blocks(
    hit_contexts: list[list[dict[str, Any]]],
) -> list[list[dict[str, Any]]]:
    """Group all hit contexts into displayable blocks of consecutive lines."""
    all_contexts = []
    for group in hit_contexts:
        all_contexts.extend(group)

    if not all_contexts:
        return []

    # Sort by line number
    sorted_ctx = sorted(all_contexts, key=lambda c: c.get("line", 0))

    blocks: list[list[dict[str, Any]]] = []
    current: list[dict[str, Any]] = [sorted_ctx[0]]

    for ctx in sorted_ctx[1:]:
        if ctx.get("line", 0) - current[-1].get("line", 0) <= 3:
            current.append(ctx)
        else:
            blocks.append(current)
            current = [ctx]
    blocks.append(current)
    return blocks


def _clean_html(text: str) -> str:
    """Strip HTML tags and entities from search result text."""
    return (
        text.replace("<em>", "")
        .replace("</em>", "")
        .replace("&quot;", '"')
        .replace("&lt;", "<")
        .replace("&gt;", ">")
        .replace("&amp;", "&")
    )
