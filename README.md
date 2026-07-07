# CargoEffe MCP Server

Connect AI assistants (Claude Desktop, Claude Code, Cursor) to CargoEffe for automated cargo loading plan design.

## Installation

```bash
# Option A: pip install
pip install cargoeffe-mcp

# Option B: uvx (no pre-install needed)
uvx cargoeffe-mcp

# Option C: from source
git clone https://github.com/dollob/cargoeffe-mcp.git
cd cargoeffe-mcp && pip install -e .
```

## Setup

1. Get your MCP token from CargoEffe Settings → MCP Tokens
2. Configure your AI client:

### Claude Code

```json
{
  "mcpServers": {
    "cargoeffe": {
      "command": "uvx",
      "args": ["cargoeffe-mcp"],
      "env": {
        "CARGOEFFE_MCP_TOKEN": "cfm_YOUR_TOKEN_HERE"
      }
    }
  }
}
```

### Claude Desktop

Add to `claude_desktop_config.json`:
```json
{
  "mcpServers": {
    "cargoeffe": {
      "command": "python",
      "args": ["-m", "cargoeffe_mcp.server"],
      "env": {
        "CARGOEFFE_MCP_TOKEN": "cfm_YOUR_TOKEN_HERE"
      }
    }
  }
}
```

## Debug Mode

Set `CARGOEFFE_MCP_DEBUG=true` for verbose logging:

```json
{
  "env": {
    "CARGOEFFE_MCP_TOKEN": "cfm_...",
    "CARGOEFFE_MCP_DEBUG": "true"
  }
}
```

Debug logs appear on stderr (visible in Claude Code's MCP debug panel).

## Available Tools

| Tool | Description |
|---|---|
| `get_context` | Read CargoEffe system context (coordinates, rules) — free |
| `get_axle_templates` | List axle templates with weight limits — free |
| `plan_create` | Create a new load plan |
| `plan_load` | Load plan by ID |
| `plan_list` | List your plans |
| `plan_save` | Save plan to backend |
| `container_list` | List available containers |
| `container_set` | Set container for a plan |
| `cargo_add` | Add cargo items (bulk) |
| `cargo_list` | List cargo items |
| `cargo_update` | Update cargo properties |
| `cargo_remove` | Delete cargo + placements |
| `group_create` | Create loading group |
| `group_list` | List loading groups |
| `group_update` | Rename/reorder groups |
| `save_placements` | Save AI-calculated placements |
| `weight_check` | Get weight distribution analysis |
| `pallet_pack_list` | List available pallet packs |
| `pallet_pack_create` | Build a pallet pack from boxes |
| `pallet_pack_place` | Place a pallet pack into a plan |

## Security

This package is a thin protocol bridge — it contains NO business logic, database queries, or API secrets. All sensitive operations happen on the CargoEffe backend.

## License

MIT
