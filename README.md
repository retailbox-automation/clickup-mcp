# ClickUp MCP Server

A Model Context Protocol (MCP) server that enables LLMs to interact with ClickUp workspaces, spaces, lists, and custom fields.

## Features

🔍 **Workspace Discovery**
- Get authenticated user information and workspace access
- List all available workspaces (teams)

📂 **Space Management**
- List all spaces in a workspace
- Get detailed space information including folders and lists
- View space status configurations

📋 **List Operations**
- Get folderless lists in a space
- View list details and task counts

🎨 **Custom Fields**
- Retrieve custom fields (columns) for any list
- View field types, configurations, and requirements
- Supports 16+ field types (text, number, dropdown, date, etc.)

## Deployment Options

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
   - Your MCP endpoint will be: `https://your-app.zeabur.app/mcp/v1/messages`

#### Connect to Web Claude

1. Open [Claude.ai](https://claude.ai)
2. Go to Settings → Integrations → MCP
3. Add a new remote server:
   ```json
   {
     "mcpServers": {
       "clickup": {
         "url": "https://your-app.zeabur.app/mcp/v1/messages",
         "transport": "sse"
       }
     }
   }
   ```

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

## Roadmap

Future enhancements:
- [ ] Task creation and updates
- [ ] Custom field value updates
- [ ] Task filtering and search
- [ ] Folder operations
- [ ] Time tracking
- [ ] Comments and updates
- [ ] Webhooks support

---

Built with ❤️ using the [Model Context Protocol](https://modelcontextprotocol.io)
