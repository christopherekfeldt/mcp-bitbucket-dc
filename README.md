# mcp-bitbucket-dc

[![PyPI Version](https://img.shields.io/pypi/v/mcp-bitbucket-dc)](https://pypi.org/project/mcp-bitbucket-dc/)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

MCP (Model Context Protocol) server for **Bitbucket Data Center**. Enables AI assistants to search code, browse files, manage pull requests, and explore repositories through a standardized interface.

Built with [FastMCP](https://github.com/jlowin/fastmcp) in Python. Installs via `uvx` — no Node.js required.

## Quick Start

### 1. Generate a Personal Access Token

1. Log in to your Bitbucket Data Center instance
2. Go to **Manage Account → HTTP access tokens**
3. Click **Create token**
4. Set permissions: **Repository Read** (and **Write** if you need PR creation/commenting)
5. Copy the token

### 2. Configure Your IDE

Add to your MCP configuration (`mcp.json` in VS Code, `claude_desktop_config.json` for Claude Desktop):

```json
{
  "mcpServers": {
    "bitbucket-dc": {
      "command": "uvx",
      "args": ["mcp-bitbucket-dc"],
      "env": {
        "BITBUCKET_HOST": "git.yourcompany.com",
        "BITBUCKET_API_TOKEN": "your-personal-access-token"
      }
    }
  }
}
```

That's it. The server starts automatically when your IDE connects.

### 3. Start Using

Ask your AI assistant:

- *"Search for CompanyInfoUpdater in the codebase"*
- *"Show me the file structure of the api-service repo in PROJECT"*
- *"Get the content of src/main/Application.java from repo backend"*
- *"List open pull requests in PROJECT/my-repo"*
- *"What branches exist in PROJECT/my-repo?"*

## Tools Reference

### Code Search (NEW)

| Tool | Description |
|---|---|
| `bitbucket_code_search` | Search code across all repos with Lucene syntax (`ext:java`, `lang:python`, `repo:name`, `project:KEY`, `AND`/`OR`/`NOT`) |

### File Browsing (NEW)

| Tool | Description |
|---|---|
| `bitbucket_browse` | Browse directory tree (files & folders at a path) |
| `bitbucket_get_file_content` | Get raw file content with syntax highlighting |
| `bitbucket_list_files` | Recursively list all file paths in a repo |
| `bitbucket_get_branches` | List branches (filterable) |
| `bitbucket_get_tags` | List tags (filterable) |

### Projects & Repositories

| Tool | Description |
|---|---|
| `bitbucket_get_projects` | List projects (filterable by name/permission) |
| `bitbucket_get_project` | Get project details |
| `bitbucket_get_repositories` | List repos in a project |
| `bitbucket_get_repository` | Get repo details with clone URLs |

### Pull Requests

| Tool | Description |
|---|---|
| `bitbucket_get_pull_requests` | List PRs (filter by state, direction, text) |
| `bitbucket_get_pull_request` | Get PR details with reviewers |
| `bitbucket_get_pull_request_comments` | Get PR comments and activity |
| `bitbucket_get_pull_request_changes` | Get files changed in a PR |
| `bitbucket_get_pull_request_diff` | Get diff for a file in a PR |
| `bitbucket_post_pull_request_comment` | Post a comment (general or inline) |
| `bitbucket_create_pull_request` | Create a new PR |
| `bitbucket_update_pull_request` | Update PR title/description/reviewers |
| `bitbucket_get_required_reviewers` | Get required reviewers for a branch pair |

### Commits

| Tool | Description |
|---|---|
| `bitbucket_get_commits` | List commits (filter by path, ref range) |

## Search Query Syntax

The `bitbucket_code_search` tool uses Lucene-style queries:

```
# Simple text search
CompanyInfoUpdater

# Filter by file extension
function ext:java

# Filter by language
config lang:python

# Filter by repository or project
DatabaseHelper repo:backend-api
service project:PLATFORM

# Filter by path
controller path:src/main

# Boolean operators (must be UPPERCASE)
config AND (yaml OR yml)
test NOT unit
UserService AND ext:java AND project:CORE
```

## Configuration

| Environment Variable | Required | Description |
|---|---|---|
| `BITBUCKET_HOST` | Yes* | Bitbucket DC hostname (e.g. `git.company.com`) |
| `BITBUCKET_URL` | Yes* | Full base URL alternative (e.g. `https://git.company.com`) |
| `BITBUCKET_API_TOKEN` | Yes | Personal Access Token |

\* Provide either `BITBUCKET_HOST` or `BITBUCKET_URL`, not both.

## Alternative Transports

```bash
# SSE transport (for remote/multi-user setups)
uvx mcp-bitbucket-dc --transport sse --port 8000

# Streamable HTTP
uvx mcp-bitbucket-dc --transport streamable-http --port 8000
```

## Development

```bash
# Clone and install
git clone https://github.com/christopherekfeldt/mcp-bitbucket-dc.git
cd mcp-bitbucket-dc
uv sync

# Run locally
export BITBUCKET_HOST=git.yourcompany.com
export BITBUCKET_API_TOKEN=your-token
uv run mcp-bitbucket-dc

# Run tests
uv run pytest
```

## License

MIT — see [LICENSE](LICENSE).
