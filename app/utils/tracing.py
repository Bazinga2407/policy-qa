import time
from contextlib import contextmanager

@contextmanager
def span(name: str, logs: dict | None = None):
    start = time.time()
    print(f"[TRACE] start {name} | {logs or {}}")
    try:
        yield
    finally:
        dur = (time.time() - start) * 1000
        print(f"[TRACE] end   {name} | {dur:.2f} ms")
