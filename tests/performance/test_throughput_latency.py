import pytest
import time
from src.nodes.queue_node import QueueNode

@pytest.mark.asyncio
async def test_queue_throughput():
    queue = QueueNode("PerfQueue")
    messages = [f"m{i}" for i in range(5000)]

    start = time.perf_counter()
    for msg in messages:
        await queue.enqueue(msg)
    for _ in messages:
        await queue.dequeue()
    end = time.perf_counter()

    duration = end - start
    throughput = len(messages) / duration
    print(f"Throughput: {throughput:.2f} msg/s")
    assert throughput > 500
