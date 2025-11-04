# ClickUp MCP Server

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![FastMCP](https://img.shields.io/badge/FastMCP-2.13+-green.svg)](https://gofastmcp.com)
[![MCP Protocol](https://img.shields.io/badge/MCP-2024--11--05-purple.svg)](https://modelcontextprotocol.io)

A production-ready Model Context Protocol (MCP) server that enables LLMs to perform comprehensive audits of ClickUp workspaces. Built with FastMCP for optimal performance and developer experience.

## 🎯 Purpose

Enable AI assistants (Claude, ChatGPT, etc.) to:
- Audit complete ClickUp workspace structures
- Analyze custom fields and data models
- Review task organization and workflows
- Discover views and dashboards
- Generate optimization recommendations

Perfect for **consultants**, **automation specialists**, and **productivity coaches** who need to analyze client ClickUp setups.

## ✨ Features

### 🔍 Workspace Discovery (3 tools)
- `get_authorized_user` - User profile and workspace memberships
- `get_spaces` - List all spaces in a workspace
- `get_space_details` - Detailed space information

### 📁 Structure Analysis (2 tools)
- `get_folders` - **Complete folder hierarchy with lists and task counts**
- `get_folderless_lists` - Lists not organized in folders

### 📋 List & Field Audit (2 tools)
- `get_list_details` - **Comprehensive list analysis with custom fields, statuses, priorities**
- `get_list_custom_fields` - Detailed custom field configuration

### 📊 Data & Views (2 tools)
- `get_tasks` - **Sample task data with custom field values (pagination)**
- `get_views` - **Views and dashboards discovery (Board, List, Calendar, Gantt, Dashboard)**

**Total: 9 powerful tools** for complete workspace audit and analysis.

## 🚀 Quick Start

### Remote (Web Claude, Claude Desktop)

Use our hosted instance - no installation required!

```json
{
  "mcpServers": {
    "clickup": {
      "url": "https://clickupmcp.zeabur.app/mcp"
    }
  }
}
```

**Note**: You need to configure `CLICKUP_API_KEY` on the server. For private deployments, see below.

### Local Installation

```bash
# Clone the repository
git clone https://github.com/retailbox-automation/clickup-mcp.git
cd clickup-mcp

# Install dependencies
pip install -r requirements.txt

# Set your API key
export CLICKUP_API_KEY="pk_your_token_here"

# Run locally
python server.py
```

---

## 🌐 Deployment Options

### Option 1: Remote SSE Server (for Web Claude)

Deploy as a remote server using SSE transport. Perfect for Zeabur, Railway, or similar platforms.

#### Deploy to Zeabur

1. **Create a new project on Zeabur**
   - Go to [Zeabur](https://zeabur.com)
   - Create a new project
   - Click "Add Service" → "Git"
   - Connect your repository

2. **Set environment variables**
   ```
   CLICKUP_API_KEY=your_clickup_api_token_here
   PORT=8000
   ```

3. **Zeabur will automatically detect Python and install dependencies**

4. **Configure the start command**
   ```bash
   python server_sse.py
   ```

5. **Get your deployment URL**
   - Zeabur will provide a URL like `https://your-app.zeabur.app`
   - Your MCP endpoint will be: `https://your-app.zeabur.app/mcp`

#### Connect to Web Claude

1. Open [Claude.ai](https://claude.ai)
2. Go to Settings → Integrations → MCP
3. Add a new remote server:
   ```json
   {
     "mcpServers": {
       "clickup": {
         "url": "https://your-app.zeabur.app/mcp"
       }
     }
   }
   ```

   **Note**: No need to specify `transport`, Claude will auto-detect HTTP Stream

### Option 2: Local Server (stdio transport)

Run locally with Claude Desktop or other MCP clients.

#### Installation

```bash
# Install dependencies
pip install -r requirements.txt

# Set your ClickUp API key
export CLICKUP_API_KEY="your_clickup_api_token_here"

# Run the server
python server.py
```

#### Configure Claude Desktop

Add to your `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "clickup": {
      "command": "python",
      "args": ["/absolute/path/to/clickup-mcp-server/server.py"],
      "env": {
        "CLICKUP_API_KEY": "your_clickup_api_token_here"
      }
    }
  }
}
```

## Getting Your ClickUp API Key

1. Go to [ClickUp Settings](https://app.clickup.com/settings/apps)
2. Click on "Apps" in the sidebar
3. Click "Generate" under "API Token"
4. Copy your Personal API Token (starts with `pk_`)

**Important**: Keep your API token secure and never commit it to version control!

## Available Tools

### `get_authorized_user`
Get information about the authenticated user including accessible workspaces.

**Example**: "Show me my ClickUp profile"

### `get_spaces`
List all spaces in a workspace.

**Parameters**:
- `team_id`: Workspace ID (get from `get_authorized_user`)
- `archived`: Include archived spaces (optional, default: false)

**Example**: "List all spaces in workspace 9012345678"

### `get_space_details`
Get comprehensive information about a specific space including folders, lists, and statuses.

**Parameters**:
- `space_id`: Space ID (get from `get_spaces`)

**Example**: "Show me details for space 90120012345"

### `get_folderless_lists`
Get lists that exist directly in a space (not in folders).

**Parameters**:
- `space_id`: Space ID
- `archived`: Include archived lists (optional, default: false)

**Example**: "Show folderless lists in space 90120012345"

### `get_list_custom_fields`
Get all custom fields (columns) configured for a list.

**Parameters**:
- `list_id`: List ID (get from `get_space_details` or `get_folderless_lists`)

**Example**: "What custom fields are on list 901200567890?"

## Supported Custom Field Types

- **Text**: `text`, `short_text`
- **Numbers**: `number`, `currency`
- **Selection**: `drop_down`, `labels`
- **Date/Time**: `date`
- **Boolean**: `checkbox`
- **Contact**: `email`, `phone`, `url`
- **Relationships**: `users`, `tasks`
- **Progress**: `automatic_progress`, `manual_progress`
- **Location**: `location`
- **Emoji**: `emoji`

## Error Handling

The server provides clear, actionable error messages:

- **401**: Authentication failed - check your API key
- **403**: Access denied - verify permissions
- **404**: Resource not found - check IDs
- **429**: Rate limit exceeded - wait and retry

## Rate Limits

ClickUp API has rate limits to protect service quality. If you hit rate limits, the server will inform you to wait before retrying.

## Character Limits

Responses are limited to 25,000 characters to optimize for LLM context windows. Larger responses will be truncated with a notice.

## Architecture

```
ClickUp Hierarchy:
Workspace (Team)
  └─ Space
      ├─ Folder
      │   └─ List
      │       ├─ Custom Fields
      │       └─ Tasks
      └─ List (folderless)
          ├─ Custom Fields
          └─ Tasks
```

## Development

### Project Structure

```
clickup-mcp-server/
├── server.py           # Stdio transport (local use)
├── server_sse.py       # SSE transport (remote deployment)
├── requirements.txt    # Python dependencies
├── README.md          # This file
└── .env.example       # Environment variables template
```

### Testing Locally

```bash
# Test SSE server
python server_sse.py

# Test health endpoint
curl http://localhost:8000/health

# Server will be available at:
# http://localhost:8000/mcp/v1/messages
```

## Security

- Never commit your `CLICKUP_API_KEY` to version control
- Use environment variables for sensitive data
- The server only makes read-only operations (all tools have `readOnlyHint: true`)
- API keys should be kept secure and rotated regularly

## Contributing

Contributions are welcome! Please feel free to submit issues or pull requests.

## License

MIT License

## Support

For issues related to:
- **ClickUp API**: [ClickUp Developer Docs](https://developer.clickup.com)
- **MCP Protocol**: [Model Context Protocol](https://modelcontextprotocol.io)
- **This Server**: Open an issue in the repository

## 📈 Use Cases

### For Consultants & Agencies
- **Client Onboarding**: Quickly audit new client ClickUp setups
- **Workflow Analysis**: Identify inefficiencies and optimization opportunities
- **Automation Planning**: Understand structure before building Make.com/Zapier flows
- **Documentation**: Auto-generate workspace structure reports

### For Internal Teams
- **Workspace Cleanup**: Find unused lists, duplicate fields, incomplete configurations
- **Standardization**: Ensure consistent field naming and structure across spaces
- **Migration Planning**: Analyze current setup before reorganization
- **Training**: Understand complex workspace hierarchies

### For Developers
- **Integration Development**: Explore API structure before building integrations
- **Data Migration**: Audit source data before migration projects
- **API Testing**: Validate ClickUp API responses and permissions

## 💼 Commercial Use

This MCP server is **open source (MIT)** and free for both personal and commercial use.

- ✅ Use for client projects
- ✅ Integrate into your consulting services
- ✅ Deploy for your organization
- ✅ Modify and customize

**Hosted Instance**: `https://clickupmcp.zeabur.app/mcp` (free during beta)

For **enterprise support** or **custom deployments**, open an issue on GitHub.

## 🐳 Docker Support

Docker is **not currently required** as:
- ✅ Zeabur natively supports Python
- ✅ FastMCP Cloud handles deployment automatically
- ✅ Simple `pip install` for local use

**Add Docker when:**
- Selling enterprise self-hosted licenses
- Need multi-tenant isolation
- Compliance/security requirements mandate containers

See `Dockerfile` (coming soon) for containerized deployment.

## 🗺️ Roadmap

### v1.1 - Enhanced Audit (Planned)
- [ ] `get_space_tags` - Space-level tag analysis
- [ ] `get_webhooks` - Existing integrations discovery
- [ ] `get_goals` - Goals and OKRs support
- [ ] `get_time_tracking` - Time tracking analytics
- [ ] `get_members` - Team member permissions

### v1.2 - Write Operations (Planned)
- [ ] Task creation and bulk updates
- [ ] Custom field value updates
- [ ] Automation management

### v2.0 - AI-Powered Features (Future)
- [ ] AI-generated optimization recommendations
- [ ] Automated cleanup suggestions
- [ ] Workflow pattern recognition
- [ ] Multi-workspace comparison

See [CHANGELOG.md](CHANGELOG.md) for detailed version history.

## 📜 License

MIT License - see [LICENSE](LICENSE) file for details.

Free for personal and commercial use. Attribution appreciated but not required.

---

## 🤝 Contributing

Contributions are welcome! Please feel free to submit issues or pull requests.

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines. (Coming soon)

---

Built with ❤️ using [FastMCP](https://gofastmcp.com) and the [Model Context Protocol](https://modelcontextprotocol.io)

**Star ⭐ this repo** if you find it useful!
