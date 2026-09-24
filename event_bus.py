import queue

_bus: queue.Queue = queue.Queue()


def post(event: dict) -> None:
    _bus.put_nowait(event)


def drain() -> list[dict]:
    events = []
    try:
        while True:
            events.append(_bus.get_nowait())
    except queue.Empty:
        pass
    return events