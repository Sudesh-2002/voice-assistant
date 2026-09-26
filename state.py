import queue
import threading
from dataclasses import dataclass, field
from datetime import datetime

STATUS_IDLE = "Idle — say 'Hey Atlas' to start"
STATUS_LISTENING = "Listening for wake word..."
STATUS_WAKE_DETECTED = "Wake word detected!"
STATUS_RECORDING = "Recording your command..."
STATUS_THINKING = "Processing..."
STATUS_SPEAKING = "Speaking..."


@dataclass
class HistoryEntry:
    timestamp: str
    user_command: str
    intent: str
    tier: str         
    reply: str


class AppState:
    def __init__(self):
        self._status = STATUS_IDLE
        self._lock = threading.Lock()

        self.history_queue: queue.Queue[HistoryEntry] = queue.Queue()

    @property
    def status(self) -> str:
        with self._lock:
            return self._status

    @status.setter
    def status(self, value: str):
        with self._lock:
            self._status = value

    def add_history(
        self,
        user_command: str,
        intent: str,
        tier: str,
        reply: str,
    ):
        entry = HistoryEntry(
            timestamp=datetime.now().strftime("%H:%M:%S"),
            user_command=user_command,
            intent=intent,
            tier=tier,
            reply=reply,
        )
        self.history_queue.put(entry)

app_state = AppState()