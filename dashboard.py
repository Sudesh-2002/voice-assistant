import customtkinter as ctk
from state import (
    app_state,
    STATUS_IDLE,
    STATUS_LISTENING,
    STATUS_WAKE_DETECTED,
    STATUS_RECORDING,
    STATUS_THINKING,
    STATUS_SPEAKING,
)

STATUS_COLORS = {
    STATUS_IDLE:          "#6b7280",
    STATUS_LISTENING:     "#2563eb",
    STATUS_WAKE_DETECTED: "#d97706",
    STATUS_RECORDING:     "#dc2626",
    STATUS_THINKING:      "#7c3aed",
    STATUS_SPEAKING:      "#059669",
}

TIER_COLORS = {
    "groq":     "#3b82f6",
    "gemini":   "#10b981",
    "deepseek": "#f59e0b",
    "none":     "#6b7280",
}

POLL_MS = 300


class Dashboard(ctk.CTk):
    def __init__(self):
        super().__init__()

        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        self.title("Atlas — Voice Assistant")
        self.geometry("520x640")
        self.resizable(False, True)
        self.configure(fg_color="#0f172a")

        self._build_header()
        self._build_status_card()
        self._build_history_section()

        self.after(POLL_MS, self._poll)

    def _build_header(self):
        header = ctk.CTkFrame(self, fg_color="#1e293b", corner_radius=0, height=60)
        header.pack(fill="x")
        header.pack_propagate(False)

        ctk.CTkLabel(
            header,
            text="🎙  ATLAS",
            font=ctk.CTkFont(family="Segoe UI", size=20, weight="bold"),
            text_color="#f1f5f9",
        ).pack(side="left", padx=20, pady=15)

        ctk.CTkLabel(
            header,
            text="Voice Assistant",
            font=ctk.CTkFont(family="Segoe UI", size=12),
            text_color="#64748b",
        ).pack(side="left", pady=15)

    def _build_status_card(self):
        card = ctk.CTkFrame(self, fg_color="#1e293b", corner_radius=12)
        card.pack(fill="x", padx=16, pady=(14, 0))

        ctk.CTkLabel(
            card,
            text="STATUS",
            font=ctk.CTkFont(family="Segoe UI", size=10, weight="bold"),
            text_color="#475569",
        ).pack(anchor="w", padx=14, pady=(10, 2))

        self._status_label = ctk.CTkLabel(
            card,
            text="● " + STATUS_IDLE,
            font=ctk.CTkFont(family="Segoe UI", size=13),
            text_color="#9ca3af",
        )
        self._status_label.pack(anchor="w", padx=14, pady=(0, 12))

    def _build_history_section(self):
        ctk.CTkLabel(
            self,
            text="COMMAND HISTORY",
            font=ctk.CTkFont(family="Segoe UI", size=10, weight="bold"),
            text_color="#475569",
        ).pack(anchor="w", padx=16, pady=(16, 4))

        self._history_frame = ctk.CTkScrollableFrame(
            self,
            fg_color="#0f172a",
            scrollbar_button_color="#334155",
            scrollbar_button_hover_color="#475569",
        )
        self._history_frame.pack(fill="both", expand=True, padx=16, pady=(0, 16))

        self._empty_label = ctk.CTkLabel(
            self._history_frame,
            text="No commands yet.\nSay 'Hey Atlas' to get started.",
            font=ctk.CTkFont(family="Segoe UI", size=13),
            text_color="#334155",
            justify="center",
        )
        self._empty_label.pack(expand=True, pady=60)
        self._has_entries = False

    def _poll(self):
        self._update_status()
        self._drain_history()
        self.after(POLL_MS, self._poll)

    def _update_status(self):
        status = app_state.status
        color = STATUS_COLORS.get(status, "#9ca3af")
        self._status_label.configure(text="● " + status, text_color=color)

    def _drain_history(self):
        while not app_state.history_queue.empty():
            try:
                entry = app_state.history_queue.get_nowait()
                self._add_card(entry)
            except Exception:
                break

    def _add_card(self, entry):
        if not self._has_entries:
            self._empty_label.destroy()
            self._has_entries = True

        tier_color = TIER_COLORS.get(entry.tier, "#6b7280")

        card = ctk.CTkFrame(self._history_frame, fg_color="#1e293b", corner_radius=10)
        card.pack(fill="x", pady=(0, 10))

        top = ctk.CTkFrame(card, fg_color="transparent")
        top.pack(fill="x", padx=12, pady=(10, 4))

        ctk.CTkLabel(
            top,
            text=entry.timestamp,
            font=ctk.CTkFont(family="Segoe UI", size=11),
            text_color="#475569",
        ).pack(side="left")

        ctk.CTkLabel(
            top,
            text=f"  {entry.tier.upper()}",
            font=ctk.CTkFont(family="Segoe UI", size=10, weight="bold"),
            text_color=tier_color,
        ).pack(side="left")

        ctk.CTkLabel(
            top,
            text=entry.intent.replace("_", " "),
            font=ctk.CTkFont(family="Segoe UI", size=10),
            text_color="#64748b",
        ).pack(side="right")

        ctk.CTkFrame(card, fg_color="#334155", height=1).pack(
            fill="x", padx=12, pady=(0, 6)
        )

        self._row(card, "You", entry.user_command, "#94a3b8")
        self._row(card, "Atlas", entry.reply, "#e2e8f0")

        self._history_frame._parent_canvas.yview_moveto(1.0)

    def _row(self, parent, label, text, color):
        row = ctk.CTkFrame(parent, fg_color="transparent")
        row.pack(fill="x", padx=12, pady=(0, 6))

        ctk.CTkLabel(
            row,
            text=f"{label}:",
            font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"),
            text_color="#64748b",
            width=40,
            anchor="w",
        ).pack(side="left", padx=(0, 6))

        ctk.CTkLabel(
            row,
            text=text,
            font=ctk.CTkFont(family="Segoe UI", size=12),
            text_color=color,
            anchor="w",
            wraplength=370,
            justify="left",
        ).pack(side="left", fill="x", expand=True)


def run_dashboard():
    app = Dashboard()
    app.mainloop()