import asyncio
from aiohttp import web
from src.utils.config import cfg
from src.consensus.raft import RaftNode, request_vote, append_entries
from src.utils.metrics import *
from prometheus_client import CONTENT_TYPE_LATEST, generate_latest

class BaseNode:
    
    def __init__(self):
        self.app = web.Application()

        self.raft = RaftNode(self.apply)
        self.app["raft"] = self.raft

        self.app.router.add_post("/raft/request_vote", request_vote)
        self.app.router.add_post("/raft/append_entries", append_entries)

        self.app.router.add_get("/health", self.health)
        self.app.router.add_get("/metrics", self.metrics)

    async def apply(self, entry):
        pass

    async def health(self, _):
        return web.json_response({
            "ok": True,
            "id": cfg.NODE_ID,
            "role": int(self.raft.role),
            "term": self.raft.current_term
        })

    async def metrics(self, _):
        return web.Response(
            body=generate_latest(),
            headers={"Content-Type": CONTENT_TYPE_LATEST}
        )

    async def start(self):
        asyncio.create_task(self.raft.tick())

        runner = web.AppRunner(self.app)
        await runner.setup()

        site = web.TCPSite(runner, "0.0.0.0", cfg.HTTP_PORT)
        await site.start()

        print(f"✅ Node {cfg.NODE_ID} listening on port {cfg.HTTP_PORT}")

        # Loop agar proses tidak mati
        try:
            while True:
                await asyncio.sleep(3600)
        except asyncio.CancelledError:
            print(f"⚠️ Node {cfg.NODE_ID} shutting down gracefully.")
