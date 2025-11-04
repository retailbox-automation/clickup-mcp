# Changelog

All notable changes to the ClickUp MCP Server will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2025-11-04

### Added

#### Core Infrastructure
- FastMCP-based server with HTTP Stream transport (streamable-http)
- Support for both stdio (local) and HTTP Stream (remote) transports
- Comprehensive error handling with actionable error messages
- Character limit enforcement (25,000 chars) for LLM context optimization
- Deployment support for Zeabur and other cloud platforms

#### Workspace Discovery Tools (5)
- `get_authorized_user` - User profile with workspace memberships
- `get_spaces` - List all spaces in a workspace
- `get_space_details` - Detailed space information with statuses
- `get_folderless_lists` - Lists not organized in folders
- `get_list_custom_fields` - Custom field configuration for lists

#### Advanced Audit Tools (4)
- `get_folders` - **Complete folder hierarchy with lists and task counts**
- `get_list_details` - **Comprehensive list analysis with all custom fields**
- `get_tasks` - **Sample task data with custom field values (pagination support)**
- `get_views` - **Views and dashboards discovery (Board, List, Calendar, Gantt, Dashboard)**

#### Documentation
- Comprehensive README.md with deployment guides
- DEPLOY.md with step-by-step Zeabur instructions
- .env.example for environment configuration
- MIT License for open source distribution

### Fixed
- URL construction bug in API requests (urljoin trailing slash issue)
- Updated from deprecated SSE to HTTP Stream transport
- Corrected endpoint paths from `/mcp/v1/messages` to `/mcp`

### Technical Details
- **Total Tools**: 9 powerful tools for complete workspace audit
- **API Version**: ClickUp API v2
- **Python Version**: 3.11+
- **Transport**: HTTP Stream (streamable-http) for remote, stdio for local
- **Endpoint**: `/mcp` for HTTP deployments

### Deployment
- Successfully deployed to Zeabur at `https://clickupmcp.zeabur.app/mcp`
- Tested and verified with Web Claude integration
- Public GitHub repository: https://github.com/retailbox-automation/clickup-mcp

---

## Roadmap

### [1.1.0] - Planned
- [ ] Space tags management (`get_space_tags`)
- [ ] Webhooks discovery (`get_webhooks`)
- [ ] Goals and OKRs support (`get_goals`)
- [ ] Time tracking analytics (`get_time_tracking`)
- [ ] Team members and permissions (`get_members`)

### [1.2.0] - Planned
- [ ] Task creation and updates
- [ ] Custom field value updates
- [ ] Bulk operations support
- [ ] Advanced filtering and search

### [2.0.0] - Future
- [ ] Write operations (create/update tasks)
- [ ] Automation management
- [ ] AI-powered recommendations
- [ ] Multi-workspace support
- [ ] Caching layer for performance

---

## Migration Guides

### Migrating from SSE to HTTP Stream
If you were using the old SSE transport, update your configuration:

**Old (SSE):**
```json
{
  "url": "https://your-server.com/sse",
  "transport": "sse"
}
```

**New (HTTP Stream):**
```json
{
  "url": "https://your-server.com/mcp"
}
```

---

[1.0.0]: https://github.com/retailbox-automation/clickup-mcp/releases/tag/v1.0.0
