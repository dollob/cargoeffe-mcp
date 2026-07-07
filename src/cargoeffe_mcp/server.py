#!/usr/bin/env python3
"""CargoEffe MCP Server — stdio transport for Claude Code / Claude Desktop.

Usage:
    cargoeffe-mcp                          # after pip install
    CARGOEFFE_API_URL=https://... cargoeffe-mcp   # with env vars

Environment variables:
    CARGOEFFE_API_URL   — CargoEffe backend URL (e.g., https://cargoeffe.com)
    CARGOEFFE_MCP_TOKEN — MCP token from Settings page (cfm_...)
    CARGOEFFE_MCP_DEBUG — Set to "true" for verbose stderr logging
"""
import os
import sys
import json
import logging
import asyncio
from typing import Optional

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

from .client import CargoEffeClient
from .tools import TOOLS

# ── Logging (stderr, not stdout — stdin/stdout are for JSON-RPC) ──
DEBUG = os.environ.get("CARGOEFFE_MCP_DEBUG", "").lower() == "true"
log_level = logging.DEBUG if DEBUG else logging.WARNING
logging.basicConfig(
    level=log_level,
    format="[%(asctime)s] %(levelname)s %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    stream=sys.stderr,
)
logger = logging.getLogger("cargoeffe-mcp")


def _check_env() -> tuple[str, str]:
    """Validate required env vars. Returns (api_url, token)."""
    api_url = os.environ.get("CARGOEFFE_API_URL", "https://cargoeffe.com").strip()
    token = os.environ.get("CARGOEFFE_MCP_TOKEN", "").strip()

    if not token:
        logger.fatal("CARGOEFFE_MCP_TOKEN is not set. Generate one at Settings → MCP Tokens.")
        sys.exit(1)
    if not token.startswith("cfm_"):
        logger.warning("Token does not start with 'cfm_'. This may not be a valid MCP token.")

    return api_url, token


async def main():
    api_url, token = _check_env()
    client = CargoEffeClient(api_url, token)

    server = Server("cargoeffe")

    @server.list_tools()
    async def list_tools() -> list[Tool]:
        logger.debug("→ tools/list")
        return TOOLS

    @server.list_prompts()
    async def list_prompts() -> list:
        """Return available prompts — auto-injected into AI context."""
        from mcp.types import Prompt
        return [
            Prompt(
                name="cargo-planning-guide",
                description="Essential CargoEffe placement strategy. Auto-injected for every session — read FIRST before placing cargo.",
                arguments=[],
            ),
            Prompt(
                name="coordinate-reference",
                description="Quick coordinate system reference: axes, dimensions, rotation quaternions, batch tips.",
                arguments=[],
            ),
        ]

    @server.get_prompt()
    async def get_prompt(name: str, arguments: dict | None = None):
        """Return prompt content."""
        if name == "cargo-planning-guide":
            return _cargo_planning_prompt()
        elif name == "coordinate-reference":
            return _coordinate_reference_prompt()
        return None

    @server.call_tool()
    async def call_tool(name: str, arguments: dict) -> list[TextContent]:
        logger.info(f"→ {name} {json.dumps(arguments, default=str)[:200]}")

        try:
            if name == "get_context":
                result = await client.get_context()
            elif name == "get_axle_templates":
                result = await client.get_axle_templates()
            elif name == "plan_create":
                result = await client.create_plan(
                    name=arguments["name"],
                    chassis_type=arguments.get("chassis_type", "rigid"),
                    region=arguments.get("region", "US"),
                    axle_template_id=arguments.get("axle_template_id"),
                    container_id=arguments.get("container_id"),
                )
            elif name == "plan_load":
                result = await client.get_plan(arguments["plan_id"])
            elif name == "plan_list":
                result = await client.list_plans()
            elif name == "plan_save":
                result = await client.save_plan(arguments["plan_id"])
            elif name == "container_list":
                result = await client.list_containers()
            elif name == "container_set":
                result = await client.set_container(arguments["plan_id"], arguments["container_id"])
            elif name == "cargo_add":
                result = await client.add_cargo(arguments["plan_id"], arguments["items"])
            elif name == "cargo_list":
                result = await client.list_cargo(arguments["plan_id"])
            elif name == "cargo_update":
                updates = {k: v for k, v in arguments.items() if k not in ("plan_id", "cargo_group_id") and v is not None}
                result = await client.update_cargo(arguments["plan_id"], arguments["cargo_group_id"], updates)
            elif name == "cargo_remove":
                result = await client.remove_cargo(arguments["plan_id"], arguments["cargo_group_id"])
            elif name == "group_create":
                result = await client.create_group(arguments["plan_id"], arguments["name"])
            elif name == "group_list":
                result = await client.list_groups(arguments["plan_id"])
            elif name == "group_update":
                updates = {k: v for k, v in arguments.items() if k not in ("plan_id", "group_id") and v is not None}
                result = await client.update_group(arguments["plan_id"], arguments["group_id"], updates)
            elif name == "save_placements":
                result = await client.save_placements(
                    arguments["plan_id"],
                    arguments.get("placements", []),
                    arguments.get("batches", []),
                    arguments.get("summary_only", False),
                    arguments.get("dry_run", False),
                )
            elif name == "weight_check":
                result = await client.weight_check(arguments["plan_id"])
            else:
                return [TextContent(type="text", text=json.dumps({"error": f"Unknown tool: {name}"}))]

            tokens_left = result.get("tokens_remaining", "?")
            logger.info(f"← {name} OK (tokens: {tokens_left})")
            if DEBUG:
                logger.debug(f"← response: {json.dumps(result, default=str)[:1000]}")

            return [TextContent(type="text", text=json.dumps(result, indent=2, default=str))]

        except Exception as e:
            error_msg = str(e)
            logger.error(f"← {name} ERROR: {error_msg}")
            return [TextContent(type="text", text=json.dumps({
                "error": error_msg,
                "tool": name,
            }, indent=2))]

    # ── Run stdio server ──
    async with stdio_server() as (read_stream, write_stream):
        logger.info("CargoEffe MCP server started")
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options(),
        )


# ── MCP Prompts — auto-injected into AI context ───────────────────────

def _cargo_planning_prompt():
    """Essential placement strategy — auto-injected at session start."""
    from mcp.types import GetPromptResult, PromptMessage, TextContent
    return GetPromptResult(
        messages=[
            PromptMessage(
                role="user",
                content=TextContent(type="text", text="""# CargoEffe Placement Strategy

## Golden Rules
1. **100% placement is the goal** — every box must be placed. Check `unplaced` after saving. If any items remain, adjust batch parameters (increase rows_per_layer, layers, or add new batches) until `unplaced` is empty.
2. **ZERO collisions** — check `collision_warnings` after EVERY save. Boxes MUST NOT overlap, interpenetrate, or share the same space. Each X,Y,Z position is occupied by exactly one box. If warnings appear, fix those specific boxes BEFORE continuing.
3. **Heaviest items FIRST** — place at Z=0 (front), Y=0 (floor). Heavy cargo near the front axle improves steering.
4. **Fill full width** — use `boxes_per_row` that covers ≥80% of container width. Heavy items (>200kg) spread across width for balance. **Use rotation** (90° around Y) to fit long items across the width when they don't fit lengthwise.
5. **Fill Z-axis fully** — use ALL available Z space within `effective_bounds.z_max`. Earlier delivery = lower Z.
6. **Stack upward aggressively** — when floor is full, stack on top (Y>0). Target >60% vertical usage. Every stacked box MUST have ≥50% bottom support. **Critical: match the row pattern below** — use same `boxes_per_row` AND `row_spacing_z` as the supporting layer. Different row spacing causes boxes to straddle edges.
7. **Respect constraints** — `noStack` boxes: nothing on top. `thisWayUp` boxes: no tilting. Different cargo types CANNOT occupy the same position.

## Batch Pattern Checklist
- `boxes_per_row` = floor(container_width / box_width) — fill the full width
- `rows_per_layer` = floor(z_max / box_length) — fill the full length
- `start_position` = [0, 0, 0] for floor layers
- Stacked layer Y = box_height_of_layer_below
- Use `dry_run=true` first (1 token) to preview collisions before committing
- **Try rotation** when a box is longer than available Z space: rotate 90° (quaternion [0,0.707,0,0.707]) to place it across X. Remember to adjust X position (box at [0.2, y, z] after rotation).

## Weight Balance Targets
- Front/Rear: 40-60% (critical if >70%)
- Left/Right: 40-60% (critical if >65%)
- If unbalanced, shift heavy batches: adjust `start_position` X or Z
- Check `weight_assessment.suggestions` for exact shift distances

## Common Mistakes
- Leaving boxes unplaced → **always re-check** `unplaced` list and add more batches to fill remaining space
- **Ignoring collision_warnings** → after EVERY save, read ALL warnings. If any overlap/floating/weak_support, fix them immediately. Split batches if only some rows have issues.
- Centering boxes (X offset > 0 without reason) → wastes space, causes left/right imbalance
- Under-filling rows (boxes_per_row too small) → right side wasted, left-biased weight
- Placing heavy items at rear → dangerous steering loss
- Not stacking → wastes 60%+ of container height
- Batch rows/layers exceeding `effective_bounds.z_max` → out-of-bounds warnings
- Different row spacing for stacked vs floor layers → each box straddles two boxes below, edges unsupported
- Stacking on misaligned rows → box edges crush into gaps between boxes below. ALWAYS match `row_spacing_z` of the supporting layer."""),
            ),
        ],
    )


def _coordinate_reference_prompt():
    """Quick coordinate + rotation reference."""
    from mcp.types import GetPromptResult, PromptMessage, TextContent
    return GetPromptResult(
        messages=[
            PromptMessage(
                role="user",
                content=TextContent(type="text", text="""# CargoEffe Coordinate Quick Reference

## Axes
- **X**: Width (0=left wall → right)
- **Y**: Height (0=floor → up)
- **Z**: Length (0=front/nose → rear)

## Container Format
`dimensions`: [length_Z, width_X, height_Y] in metres

## Position
`[X, Y, Z]` = left-bottom-front corner of the box

## Rotation (Quaternion [qx, qy, qz, qw])
- Default: `[0, 0, 0, 1]` = length along Z
- 90° right: `[0, 0.707, 0, 0.707]` = length along X
- 90° left: `[0, -0.707, 0, 0.707]` = length along X
- ⚠️ Rotated boxes shift! A 1.2×0.8m box rotated 90° at [0,0,0] goes to X=-0.2. Use X≥0.2 to stay in bounds.

## Key Constraints
- `thisWayUp`: box cannot tilt (only Y-axis rotations)
- `noStack`: nothing can be placed on top
- `effective_bounds.z_max`: actual deck length (may differ from container length)
- `effective_bounds.y_max`: container height limit

## Batch Quick Reference
```json
{
  "cargoGroupId": "cg-xxx",
  "count": 40,
  "start_position": [0, 0, 0],
  "boxes_per_row": 8,
  "rows_per_layer": 5,
  "layers": 2,
  "layer_spacing_y": 0.25
}
```"""),
            ),
        ],
    )


def cli():
    """Entry point for 'cargoeffe-mcp' console script."""
    asyncio.run(main())


if __name__ == "__main__":
    cli()
