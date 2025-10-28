import asyncio
import random
import time
from typing import Dict, List, Any


class PBFTConsensus:
    def __init__(self, node_id: str, peers: List[str], broker_send=None, broker_subscribe=None):
        self.node_id = node_id
        self.peers = peers
        self.broker_send = broker_send
        self.broker_subscribe = broker_subscribe

        self.view = 0
        self.primary = self._get_primary()
        self.prepared: Dict[str, Any] = {}
        self.committed: Dict[str, Any] = {}

    def _get_primary(self) -> str:
        if not self.peers:
            return self.node_id
        return self.peers[self.view % len(self.peers)]

    async def start(self):
        if self.broker_subscribe:
            await self.broker_subscribe(self.node_id, self._on_message)

    async def _on_message(self, message):
        content = message.content
        mtype = content.get("type")
        if mtype == "pre-prepare":
            for p in self.peers:
                await self.broker_send(
                    type("M", (), {})()
                )
