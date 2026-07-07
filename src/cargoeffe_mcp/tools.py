"""MCP tool definitions with JSON Schema inputs for CargoEffe operations."""
from mcp.types import Tool

TOOLS: list[Tool] = [
    Tool(
        name="get_context",
        description="Read CargoEffe system context document. Use this FIRST to understand the coordinate system, placement conventions, rotation rules, and regulatory guidelines. Free — no token cost.",
        inputSchema={
            "type": "object",
            "properties": {},
        },
    ),
    Tool(
        name="get_axle_templates",
        description="List all available axle templates with their full configuration (axle groups, positions, weight limits per region). Use this to understand weight constraints before placing cargo. Free — no token cost.",
        inputSchema={
            "type": "object",
            "properties": {},
        },
    ),
    Tool(
        name="plan_create",
        description="Create a new cargo loading plan. Specify chassis type (container/rigid/articulated), regulatory region (US/EU/HK), and optionally an axle template and container.",
        inputSchema={
            "type": "object",
            "properties": {
                "name": {"type": "string", "description": "Plan name"},
                "chassis_type": {
                    "type": "string",
                    "enum": ["container", "rigid", "articulated"],
                    "description": "Chassis type. 'rigid' = single truck, 'articulated' = tractor+trailer",
                },
                "region": {
                    "type": "string",
                    "enum": ["US", "EU", "HK"],
                    "description": "Regulatory region for weight limits",
                },
                "axle_template_id": {
                    "type": "string",
                    "description": "Optional axle template ID from get_axle_templates",
                },
                "container_id": {
                    "type": "string",
                    "description": "Optional container ID from container_list",
                },
            },
            "required": ["name"],
        },
    ),
    Tool(
        name="plan_load",
        description="Load a plan by its ID. Returns full state: container, cargo items, placements, loading groups, axle config.",
        inputSchema={
            "type": "object",
            "properties": {
                "plan_id": {"type": "string", "description": "Plan ID (e.g., 'plan-abc123')"},
            },
            "required": ["plan_id"],
        },
    ),
    Tool(
        name="plan_list",
        description="List all your saved load plans.",
        inputSchema={
            "type": "object",
            "properties": {},
        },
    ),
    Tool(
        name="plan_save",
        description="Persist the current plan state to the backend.",
        inputSchema={
            "type": "object",
            "properties": {
                "plan_id": {"type": "string", "description": "Plan ID to save"},
            },
            "required": ["plan_id"],
        },
    ),
    Tool(
        name="container_list",
        description="List all available containers (standard sizes + your custom containers) with dimensions and max weight.",
        inputSchema={
            "type": "object",
            "properties": {},
        },
    ),
    Tool(
        name="container_set",
        description="Set or change the container for a plan.",
        inputSchema={
            "type": "object",
            "properties": {
                "plan_id": {"type": "string", "description": "Plan ID"},
                "container_id": {"type": "string", "description": "Container ID from container_list"},
            },
            "required": ["plan_id", "container_id"],
        },
    ),
    Tool(
        name="cargo_add",
        description="Add cargo items to a plan. Supports bulk creation — send an array of cargo specifications. Dimensions in cm (converted to metres internally).",
        inputSchema={
            "type": "object",
            "properties": {
                "plan_id": {"type": "string", "description": "Plan ID"},
                "items": {
                    "type": "array",
                    "description": "Array of cargo items to add",
                    "items": {
                        "type": "object",
                        "properties": {
                            "name": {"type": "string", "description": "Cargo item name"},
                            "length_cm": {"type": "number", "description": "Box length in centimetres (along Z axis)"},
                            "width_cm": {"type": "number", "description": "Box width in centimetres (along X axis)"},
                            "height_cm": {"type": "number", "description": "Box height in centimetres (along Y axis)"},
                            "weight_kg": {"type": "number", "description": "Weight per box in kg"},
                            "quantity": {"type": "integer", "description": "Number of boxes of this type"},
                            "color_hex": {"type": "string", "description": "Hex color for 3D display, e.g., '#FF6B6B'"},
                            "loading_group": {"type": "string", "description": "Loading group name or ID (first-in-last-out priority)"},
                            "this_way_up": {"type": "boolean", "description": "Box must remain upright (no tilting)"},
                            "no_stack": {"type": "boolean", "description": "Nothing can be placed on top of this box"},
                            "no_roll": {"type": "boolean", "description": "Box cannot rotate (same as this_way_up)"},
                            "metadata": {"type": "string", "description": "Optional metadata (SKU, notes, etc.)"},
                        },
                        "required": ["name", "length_cm", "width_cm", "height_cm", "weight_kg", "quantity"],
                    },
                },
            },
            "required": ["plan_id", "items"],
        },
    ),
    Tool(
        name="cargo_list",
        description="List all cargo items in a plan with their dimensions, weight, quantity, placed count, and loading group.",
        inputSchema={
            "type": "object",
            "properties": {
                "plan_id": {"type": "string", "description": "Plan ID"},
            },
            "required": ["plan_id"],
        },
    ),
    Tool(
        name="cargo_update",
        description="Update a cargo item's properties (name, dimensions, weight, quantity, color, flags, loading_group).",
        inputSchema={
            "type": "object",
            "properties": {
                "plan_id": {"type": "string", "description": "Plan ID"},
                "cargo_group_id": {"type": "string", "description": "Cargo item ID to update"},
                "name": {"type": "string", "description": "New name"},
                "length_cm": {"type": "number", "description": "New length in cm"},
                "width_cm": {"type": "number", "description": "New width in cm"},
                "height_cm": {"type": "number", "description": "New height in cm"},
                "weight_kg": {"type": "number", "description": "New weight per box in kg"},
                "quantity": {"type": "integer", "description": "New total quantity"},
                "color_hex": {"type": "string", "description": "New hex color"},
                "loading_group": {"type": "string", "description": "New loading group name or ID"},
                "this_way_up": {"type": "boolean"},
                "no_stack": {"type": "boolean"},
                "no_roll": {"type": "boolean"},
                "metadata": {"type": "string"},
            },
            "required": ["plan_id", "cargo_group_id"],
        },
    ),
    Tool(
        name="cargo_remove",
        description="Remove a cargo item and ALL its placed boxes from the plan.",
        inputSchema={
            "type": "object",
            "properties": {
                "plan_id": {"type": "string", "description": "Plan ID"},
                "cargo_group_id": {"type": "string", "description": "Cargo item ID to remove"},
            },
            "required": ["plan_id", "cargo_group_id"],
        },
    ),
    Tool(
        name="group_create",
        description="Create a loading group for cargo priority ordering. Lower order = loaded first (deeper), higher order = loaded last (near doors).",
        inputSchema={
            "type": "object",
            "properties": {
                "plan_id": {"type": "string", "description": "Plan ID"},
                "name": {"type": "string", "description": "Group name, e.g., 'First Load' or 'Last Load'"},
            },
            "required": ["plan_id", "name"],
        },
    ),
    Tool(
        name="group_list",
        description="List all loading groups in a plan with their order (priority).",
        inputSchema={
            "type": "object",
            "properties": {
                "plan_id": {"type": "string", "description": "Plan ID"},
            },
            "required": ["plan_id"],
        },
    ),
    Tool(
        name="group_update",
        description="Rename or reorder a loading group.",
        inputSchema={
            "type": "object",
            "properties": {
                "plan_id": {"type": "string", "description": "Plan ID"},
                "group_id": {"type": "string", "description": "Group ID to update"},
                "name": {"type": "string", "description": "New group name"},
                "order": {"type": "integer", "description": "New group order (0 = first loaded, higher = last loaded)"},
            },
            "required": ["plan_id", "group_id"],
        },
    ),
    Tool(
        name="save_placements",
        description="""Save AI-calculated box placements. ALWAYS replaces all existing placements — send the complete list every time.

CRITICAL — Understand the coordinate system before using:
- Container dimensions: [length_Z, width_X, height_Y] in metres
- Position [X, Y, Z] = left-bottom-front corner of the box
- Rotation [qx, qy, qz, qw]: default [0,0,0,1] = length along Z
- For 90° rotation around Y: [0, 0.707, 0, 0.707] = length along X

Use BATCHES for efficiency! Instead of listing every box position, describe row/layer patterns:
- boxes_per_row: how many fit across the width (X axis)
- rows_per_layer: how many rows fit along the length (Z axis)
- layers: how many stacked layers (Y axis)
- box_spacing_x, row_spacing_z, layer_spacing_y: centre-to-centre spacing
- The server auto-generates all individual positions from the pattern.

Strategy: Place largest/heaviest first at Z=0, Y=0. Fill left-to-right, then front-to-back. Stack lighter items on top. Server returns collision warnings — fix specific boxes and retry.""",
        inputSchema={
            "type": "object",
            "properties": {
                "plan_id": {"type": "string", "description": "Plan ID"},
                "placements": {
                    "type": "array",
                    "description": "Individual box placements (use for special positions or small numbers)",
                    "items": {
                        "type": "object",
                        "properties": {
                            "cargoGroupId": {"type": "string", "description": "Cargo item ID from cargo_list"},
                            "position": {"type": "array", "items": {"type": "number"}, "minItems": 3, "maxItems": 3, "description": "[X, Y, Z] position in metres"},
                            "rotation": {"type": "array", "items": {"type": "number"}, "minItems": 4, "maxItems": 4, "description": "[qx, qy, qz, qw] quaternion rotation"},
                        },
                        "required": ["cargoGroupId", "position"],
                    },
                },
                "summary_only": {"type": "boolean", "description": "Set true for compact response (recommended for >50 boxes). Omits individual placements, returns summary + assessment."},
                "dry_run": {"type": "boolean", "description": "Validate without saving. Costs 1 token instead of 5. Returns collisions + assessment without modifying plan state."},
                "batches": {
                    "type": "array",
                    "description": "Batch placements — describe grid patterns for large quantities (MUCH more efficient)",
                    "items": {
                        "type": "object",
                        "properties": {
                            "cargoGroupId": {"type": "string", "description": "Cargo item ID from cargo_list"},
                            "count": {"type": "integer", "description": "Number of boxes to place in this batch"},
                            "start_position": {"type": "array", "items": {"type": "number"}, "minItems": 3, "maxItems": 3, "description": "[X, Y, Z] of the first box (left-bottom-front corner)"},
                            "boxes_per_row": {"type": "integer", "description": "Boxes per row along X (width). Auto-calculated from container width if omitted."},
                            "rows_per_layer": {"type": "integer", "description": "Rows per layer along Z (length). Auto-calculated from container length if omitted."},
                            "layers": {"type": "integer", "description": "Number of stacked layers. Default 1."},
                            "box_spacing_x": {"type": "number", "description": "Centre-to-centre X spacing. Defaults to box width (snug fit)."},
                            "row_spacing_z": {"type": "number", "description": "Centre-to-centre Z spacing. Defaults to box length (snug fit)."},
                            "layer_spacing_y": {"type": "number", "description": "Centre-to-centre Y stacking spacing. Defaults to box height."},
                            "rotation": {"type": "array", "items": {"type": "number"}, "minItems": 4, "maxItems": 4, "description": "Quaternion rotation for all boxes in this batch"},
                        },
                        "required": ["cargoGroupId", "count", "start_position"],
                    },
                },
            },
            "required": ["plan_id"],
        },
    ),
    Tool(
        name="weight_check",
        description="Compute and return weight distribution analysis: COG, axle loads, GVW, steer axle %, bridge formula result, regulatory pass/fail status.",
        inputSchema={
            "type": "object",
            "properties": {
                "plan_id": {"type": "string", "description": "Plan ID"},
            },
            "required": ["plan_id"],
        },
    ),
]
