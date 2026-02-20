"""Tests for formatting helpers."""

from __future__ import annotations

from mcp_bitbucket_dc.formatting import (
    format_branches,
    format_browse,
    format_commits,
    format_projects,
    format_pull_requests,
    format_repositories,
    format_search_results,
)


class TestFormatProjects:
    def test_formats_project_list(self):
        projects = [
            {"key": "PROJ", "name": "My Project", "public": True, "description": "A test project"},
            {"key": "INT", "name": "Internal", "public": False},
        ]
        result = format_projects(projects, total=2, is_last=True)
        assert "My Project" in result
        assert "PROJ" in result
        assert "Public" in result
        assert "Internal" in result

    def test_shows_pagination_hint(self):
        result = format_projects([], total=50, is_last=False)
        assert "More projects available" in result


class TestFormatSearchResults:
    def test_formats_search_hit(self):
        results = [
            {
                "repository": {"name": "backend", "project": {"key": "PROJ"}},
                "file": "src/main/App.java",
                "hitCount": 3,
                "hitContexts": [
                    [{"line": 10, "text": "public class <em>App</em> {"}]
                ],
            }
        ]
        md = format_search_results(results, query="App", total=1, is_last=True)
        assert "App.java" in md
        assert "backend" in md
        assert "PROJ" in md
        assert "public class App {" in md  # HTML tags stripped

    def test_empty_results(self):
        md = format_search_results([], query="nothing", total=0, is_last=True)
        assert "0" in md


class TestFormatBrowse:
    def test_directory_listing(self):
        data = {
            "children": {
                "size": 2,
                "isLastPage": True,
                "values": [
                    {"path": {"toString": "src"}, "type": "DIRECTORY"},
                    {"path": {"toString": "README.md"}, "type": "FILE", "size": 1024},
                ],
            }
        }
        result = format_browse(data, path="/")
        assert "src/" in result
        assert "README.md" in result
        assert "📁" in result
        assert "📄" in result
