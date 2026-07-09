"""HTTP client for CargoEffe MCP REST API."""
import json
import httpx
from typing import Optional


class CargoEffeClient:
    """Async HTTP client wrapping CargoEffe's /api/mcp/ endpoints."""

    def __init__(self, base_url: str, token: str, timeout: int = 60):
        self.base = f"{base_url.rstrip('/')}/api/mcp"
        self.headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        }
        self.timeout = timeout

    async def _get(self, path: str) -> dict:
        async with httpx.AsyncClient(timeout=self.timeout) as c:
            r = await c.get(f"{self.base}{path}", headers=self.headers)
            r.raise_for_status()
            return r.json()

    async def _post(self, path: str, data: Optional[dict] = None) -> dict:
        async with httpx.AsyncClient(timeout=self.timeout) as c:
            r = await c.post(f"{self.base}{path}", json=data or {}, headers=self.headers)
            r.raise_for_status()
            return r.json()

    async def _put(self, path: str, data: dict) -> dict:
        async with httpx.AsyncClient(timeout=self.timeout) as c:
            r = await c.put(f"{self.base}{path}", json=data, headers=self.headers)
            r.raise_for_status()
            return r.json()

    async def _delete(self, path: str) -> dict:
        async with httpx.AsyncClient(timeout=self.timeout) as c:
            r = await c.delete(f"{self.base}{path}", headers=self.headers)
            r.raise_for_status()
            return r.json()

    # ── System Context ──

    async def get_context(self) -> dict:
        return await self._get("/context")

    async def get_axle_templates(self) -> dict:
        return await self._get("/axle-templates")

    # ── Containers ──

    async def list_containers(self) -> dict:
        return await self._get("/containers")

    # ── Plans ──

    async def list_plans(self) -> dict:
        return await self._get("/plans")

    async def create_plan(
        self,
        name: str,
        chassis_type: str = "rigid",
        region: str = "US",
        axle_template_id: Optional[str] = None,
        container_id: Optional[str] = None,
    ) -> dict:
        return await self._post("/plans", {
            "name": name,
            "chassis_type": chassis_type,
            "region": region,
            "axle_template_id": axle_template_id,
            "container_id": container_id,
        })

    async def get_plan(self, plan_id: str) -> dict:
        return await self._get(f"/plans/{plan_id}")

    async def save_plan(self, plan_id: str) -> dict:
        return await self._post(f"/plans/{plan_id}/save")

    async def set_container(self, plan_id: str, container_id: str) -> dict:
        return await self._put(f"/plans/{plan_id}/container", {"container_id": container_id})

    async def create_container(self, name: str, length_cm: float, width_cm: float, height_cm: float, max_weight_kg: float = None) -> dict:
        params = {"name": name, "length_cm": length_cm, "width_cm": width_cm, "height_cm": height_cm}
        if max_weight_kg:
            params["max_weight_kg"] = max_weight_kg
        return await self._post(f"/containers/custom?{'&'.join(f'{k}={v}' for k,v in params.items())}")

    # ── Cargo Items ──

    async def list_cargo(self, plan_id: str) -> dict:
        return await self._get(f"/plans/{plan_id}/cargo")

    async def add_cargo(self, plan_id: str, items: list[dict]) -> dict:
        return await self._post(f"/plans/{plan_id}/cargo", {"items": items})

    async def update_cargo(self, plan_id: str, cg_id: str, updates: dict) -> dict:
        return await self._put(f"/plans/{plan_id}/cargo/{cg_id}", updates)

    async def remove_cargo(self, plan_id: str, cg_id: str) -> dict:
        return await self._delete(f"/plans/{plan_id}/cargo/{cg_id}")

    # ── Loading Groups ──

    async def list_groups(self, plan_id: str) -> dict:
        return await self._get(f"/plans/{plan_id}/groups")

    async def create_group(self, plan_id: str, name: str) -> dict:
        return await self._post(f"/plans/{plan_id}/groups", {"name": name})

    async def update_group(self, plan_id: str, group_id: str, updates: dict) -> dict:
        return await self._put(f"/plans/{plan_id}/groups/{group_id}", updates)

    # ── Placements ──

    async def save_placements(self, plan_id: str, placements: list[dict] = None, batches: list[dict] = None, summary_only: bool = False, dry_run: bool = False) -> dict:
        body = {"placements": placements or [], "batches": batches or [], "summary_only": summary_only, "dry_run": dry_run}
        return await self._put(f"/plans/{plan_id}/placements", body)

    # ── Weight ──

    async def weight_check(self, plan_id: str) -> dict:
        return await self._get(f"/plans/{plan_id}/weight")

    # ── Axle Templates ──

    async def create_axle_template(self, data: dict) -> dict:
        return await self._post("/axle-templates", data)

    # ── Pallet Packs ──

    async def list_pallet_packs(self) -> dict:
        return await self._get("/pallet-packs")

    async def create_pallet_pack(self, data: dict) -> dict:
        return await self._post("/pallet-packs", data)

    async def place_pallet_pack(self, plan_id: str, pallet_pack_id: str, position: list, quantity: int = 1, loading_group: str = None, spread: bool = True) -> dict:
        body = {
            "pallet_pack_id": pallet_pack_id,
            "position": position,
            "quantity": quantity,
            "spread": spread,
        }
        if loading_group:
            body["loading_group"] = loading_group
        return await self._post(f"/plans/{plan_id}/pallet-packs", body)
