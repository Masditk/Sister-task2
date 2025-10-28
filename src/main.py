import asyncio
from src.utils.config import cfg

async def start_queue_node():
    print("Simulasi: Distributed Queue Node (tidak diinisialisasi untuk mencegah heartbeat)...", flush=True)
    await asyncio.sleep(0)


async def start_lock_node():
    print("Simulasi: Raft Distributed Lock Node (tidak diinisialisasi untuk mencegah heartbeat)...", flush=True)
    print(f"Node {cfg.NODE_ID} terinisialisasi di port {cfg.HTTP_PORT} [mode diam]", flush=True)
    await asyncio.sleep(0)


async def start_cache_node():
    print("Simulasi: Distributed Cache Node (tidak diinisialisasi untuk mencegah heartbeat)...", flush=True)
    await asyncio.sleep(0)


async def main():
    tasks = [
        asyncio.create_task(start_queue_node()),
        asyncio.create_task(start_lock_node()),
        asyncio.create_task(start_cache_node())
    ]

    print("Semua node dalam mode diam — tidak ada heartbeat, tidak ada Raft loop.", flush=True)
    await asyncio.gather(*tasks)

    print("Simulasi selesai tanpa aktivitas jaringan.", flush=True)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception as e:
        print(f"Fatal error: {e}", flush=True)
