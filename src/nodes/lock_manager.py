from aiohttp import web
import asyncio
from src.nodes.base_node import BaseNode
from src.utils.metrics import locks_acquired, locks_blocked

lock_table = {}

class LockNode(BaseNode):
    def __init__(self):
        super().__init__()
        self.app.router.add_post("/lock/acquire", self.acquire)
        self.app.router.add_post("/lock/release", self.release)
        self.waiters = {}

    async def apply(self, entry):
        entry_type = entry.get("type")

        if entry_type == "LOCK_ACQUIRE":
            key = entry["key"]
            mode = entry["mode"]
            client_id = entry["client_id"]

            state = lock_table.setdefault(key, {"mode": None, "holders": set(), "queue": []})

            if (state["mode"] in (None, "S")) and mode == "S" and (
                state["mode"] is None or "X" not in state["holders"]
            ):
                state["mode"] = "S"
                state["holders"].add(client_id)
                locks_acquired.labels("S").inc()

            elif state["mode"] is None and mode == "X":
                state["mode"] = "X"
                state["holders"].add(client_id)
                locks_acquired.labels("X").inc()

            else:
                state["queue"].append((mode, client_id))
                locks_blocked.labels(mode).inc()

        elif entry_type == "LOCK_RELEASE":
            key = entry["key"]
            client_id = entry["client_id"]

            state = lock_table.get(key)
            if not state:
                return

            if client_id in state["holders"]:
                state["holders"].remove(client_id)

                if not state["holders"]:
                    state["mode"] = None

                    while state["queue"]:
                        mode, c = state["queue"][0]

                        queued_clients = [cid for _, cid in state["queue"]]
                        if len(queued_clients) != len(set(queued_clients)):
                            print(
                                f"⚠️ Possible DEADLOCK detected on key '{key}' "
                                f"involving clients {queued_clients}",
                                flush=True,
                            )

                        if mode == "S":
                            s_can = [(m, cc) for (m, cc) in state["queue"] if m == "S"]
                            for _, cc in s_can:
                                state["queue"].remove(("S", cc))
                            state["mode"] = "S"
                            state["holders"].update({cc for _, cc in s_can})
                        else:
                            state["queue"].pop(0)
                            state["mode"] = "X"
                            state["holders"].add(c)
                        break

    async def acquire(self, req: web.Request):
        data = await req.json()
        entry = {
            "type": "LOCK_ACQUIRE",
            "key": data["key"],
            "mode": data["mode"],
            "client_id": data["client_id"],
        }

        if self.raft.role != 2:
            return web.json_response({"redirect": self.raft.leader_hint}, status=307)

        ok = await self.raft.replicate_and_commit(entry)
        return web.json_response({"ok": ok})

    async def release(self, req: web.Request):
        data = await req.json()
        entry = {
            "type": "LOCK_RELEASE",
            "key": data["key"],
            "client_id": data["client_id"],
        }

        if self.raft.role != 2:
            return web.json_response({"redirect": self.raft.leader_hint}, status=307)

        ok = await self.raft.replicate_and_commit(entry)
        return web.json_response({"ok": ok})
