import threading
from datetime import datetime
import customtkinter as ctk

import event_bus

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

STATUS_COLORS = {
    "listening":  "#2ecc71", 
    "processing": "#f39c12", 
    "idle":       "#7f8c8d", 
}

STATUS_LABELS = {
    "listening":  "● Listening",
    "processing": "⟳ Processing",
    "idle":       "○ Idle",
}


class AtlasDashboard(ctk.CTk):
    def __init__(self, stop_event: threading.Event):
        super().__init__()
        self.stop_event = stop_event

        self.title("Atlas — Voice Assistant")
        self.geometry("560x680")
        self.resizable(True, True)

        self._build_ui()
        self._poll_events()

    def _build_ui(self):
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=20, pady=(20, 0))

        ctk.CTkLabel(
            header, text="Atlas", font=ctk.CTkFont(size=28, weight="bold")
        ).pack(side="left")

        self.status_label = ctk.CTkLabel(
            header,
            text=STATUS_LABELS["idle"],
            font=ctk.CTkFont(size=14),
            text_color=STATUS_COLORS["idle"],
        )
        self.status_label.pack(side="right", padx=4)

        ctk.CTkFrame(self, height=2, fg_color="#2b2b2b").pack(
            fill="x", padx=20, pady=12
        )

        ctk.CTkLabel(
            self,
            text="Command History",
            font=ctk.CTkFont(size=13, weight="bold"),
            anchor="w",
        ).pack(fill="x", padx=20, pady=(0, 6))

        self.history_frame = ctk.CTkScrollableFrame(
            self, fg_color="#1a1a1a", corner_radius=10
        )
        self.history_frame.pack(fill="both", expand=True, padx=20, pady=(0, 12))

        ctk.CTkButton(
            self,
            text="Clear History",
            width=140,
            height=32,
            fg_color="#333333",
            hover_color="#444444",
            command=self._clear_history,
        ).pack(pady=(0, 16))

    def _poll_events(self):
        for event in event_bus.drain():
            etype = event.get("type")
            if etype == "status":
                self._set_status(event["value"])
            elif etype == "command":
                self._add_command_card(event)
            elif etype == "reply":
                self._add_reply_card(event["text"])

        if self.stop_event.is_set():
            self.destroy()
            return

        self.after(200, self._poll_events)

    def _set_status(self, status: str):
        self.status_label.configure(
            text=STATUS_LABELS.get(status, status),
            text_color=STATUS_COLORS.get(status, "#ffffff"),
        )

    def _add_command_card(self, event: dict):
        """Adds a 'You said' card to the history."""
        timestamp = datetime.now().strftime("%H:%M:%S")
        card = ctk.CTkFrame(self.history_frame, fg_color="#252525", corner_radius=8)
        card.pack(fill="x", pady=4, padx=4)

        top = ctk.CTkFrame(card, fg_color="transparent")
        top.pack(fill="x", padx=10, pady=(8, 2))
        ctk.CTkLabel(
            top, text=timestamp,
            font=ctk.CTkFont(size=11), text_color="#666666"
        ).pack(side="left")
        tier = event.get("tier", "")
        if tier:
            ctk.CTkLabel(
                top, text=f"via {tier}",
                font=ctk.CTkFont(size=11), text_color="#3b82f6"
            ).pack(side="right")

        ctk.CTkLabel(
            card, text=f"You:  {event.get('text', '')}",
            font=ctk.CTkFont(size=13), anchor="w", wraplength=480
        ).pack(fill="x", padx=10, pady=(0, 2))

        intent = event.get("intent", "")
        if intent and intent != "unknown":
            ctk.CTkLabel(
                card,
                text=f"Intent: {intent.replace('_', ' ')}",
                font=ctk.CTkFont(size=11),
                text_color="#10b981",
                anchor="w",
            ).pack(fill="x", padx=10, pady=(0, 8))

        self._scroll_to_bottom()

    def _add_reply_card(self, text: str):
        card = ctk.CTkFrame(
            self.history_frame, fg_color="#1e3a5f", corner_radius=8
        )
        card.pack(fill="x", pady=(0, 8), padx=4)
        ctk.CTkLabel(
            card,
            text=f"Atlas:  {text}",
            font=ctk.CTkFont(size=13),
            anchor="w",
            wraplength=480,
            text_color="#93c5fd",
        ).pack(fill="x", padx=10, pady=10)
        self._scroll_to_bottom()

    def _scroll_to_bottom(self):
        self.history_frame._parent_canvas.yview_moveto(1.0)

    def _clear_history(self):
        for widget in self.history_frame.winfo_children():
            widget.destroy()


def run_dashboard(stop_event: threading.Event):
    app = AtlasDashboard(stop_event)
    app.mainloop()