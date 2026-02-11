import json
import os
import uuid
import tkinter as tk
from dataclasses import dataclass, asdict
from tkinter import ttk
from tkinter import font as tkfont
from typing import Dict, List, Optional

DATA_FILE = "todo_data.json"
XP_PER_WEIGHT = 10
XP_PER_LEVEL = 100

COLORS = {
    "sky_top": "#9ed8ff",
    "sky_bottom": "#6fb7f1",
    "sea_dark": "#1f5d9b",
    "sea_light": "#2b78c7",
    "island_sand": "#f1d48a",
    "island_grass": "#5dbb63",
    "panel": "#1a2a3a",
    "panel_border": "#4e6a7d",
    "text": "#e7f6ff",
    "muted": "#b8d0e0",
    "accent": "#ffcc4d",
    "accent_dark": "#c89b2e",
}


@dataclass
class Task:
    id: str
    text: str
    weight: int
    completed: bool = False
    completed_at: Optional[str] = None


class TodoApp:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("Island Todo Quest")
        self.root.geometry("960x600")
        self.root.minsize(840, 520)

        self.font_title = tkfont.Font(family="Lucida Console", size=18, weight="bold")
        self.font_body = tkfont.Font(family="Consolas", size=10)
        self.font_small = tkfont.Font(family="Consolas", size=9)
        self.font_strike = tkfont.Font(family="Consolas", size=10, overstrike=1)

        self.tasks: Dict[str, Task] = {}
        self.history: List[Task] = []
        self.xp_total = 0

        self.canvas = tk.Canvas(self.root, highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True)
        self.canvas.bind("<Configure>", self.on_resize)

        # Overlay frame for level-up animation (sits on top of everything)
        self.overlay_frame = None
        self.overlay_canvas = None

        self.hud_frame = tk.Frame(self.canvas, bg=COLORS["panel"], bd=2, relief=tk.RIDGE)
        self.todo_frame = tk.Frame(self.canvas, bg=COLORS["panel"], bd=2, relief=tk.RIDGE)
        self.history_frame = tk.Frame(self.canvas, bg=COLORS["panel"], bd=2, relief=tk.RIDGE)
        self.xp_frame = tk.Frame(self.canvas, bg=COLORS["panel"], bd=2, relief=tk.RIDGE)

        self.hud_window = self.canvas.create_window(0, 0, window=self.hud_frame, anchor="nw")
        self.todo_window = self.canvas.create_window(0, 0, window=self.todo_frame, anchor="nw")
        self.history_window = self.canvas.create_window(0, 0, window=self.history_frame, anchor="nw")
        self.xp_window = self.canvas.create_window(0, 0, window=self.xp_frame, anchor="nw")

        self.build_hud()
        self.build_todo_panel()
        self.build_history_panel()
        self.build_xp_panel()

        self.load_data()
        self.refresh_task_list()
        self.refresh_history_list()
        self.update_xp_bar()

        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

    def build_hud(self) -> None:
        label = tk.Label(
            self.hud_frame,
            text="Island Todo Quest",
            font=self.font_title,
            fg=COLORS["accent"],
            bg=COLORS["panel"],
        )
        label.pack(padx=12, pady=8)

        self.level_label = tk.Label(
            self.hud_frame,
            text="Level 1",
            font=self.font_body,
            fg=COLORS["text"],
            bg=COLORS["panel"],
        )
        self.level_label.pack(padx=12, pady=(0, 8))

    def build_todo_panel(self) -> None:
        header = tk.Label(
            self.todo_frame,
            text="Active Quests",
            font=self.font_body,
            fg=COLORS["text"],
            bg=COLORS["panel"],
        )
        header.pack(anchor="w", padx=10, pady=(8, 4))

        add_row = tk.Frame(self.todo_frame, bg=COLORS["panel"])
        add_row.pack(fill=tk.X, padx=10, pady=(0, 8))

        self.new_task_text = tk.Entry(add_row, font=self.font_body)
        self.new_task_text.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 6))
        self.new_task_text.bind("<Return>", lambda e: self.add_task())
        self.new_task_text.bind("<Up>", lambda e: self.increment_weight(1))
        self.new_task_text.bind("<Down>", lambda e: self.increment_weight(-1))

        self.new_weight_var = tk.IntVar(value=2)
        self.new_weight_spin = tk.Spinbox(
            add_row,
            from_=1,
            to=5,
            width=3,
            textvariable=self.new_weight_var,
            font=self.font_body,
        )
        self.new_weight_spin.pack(side=tk.LEFT, padx=(0, 6))
        self.new_weight_spin.bind("<Return>", lambda e: self.add_task())

        add_btn = tk.Button(
            add_row,
            text="Add",
            font=self.font_body,
            command=self.add_task,
            bg=COLORS["accent"],
            fg="#000000",
            activebackground=COLORS["accent_dark"],
        )
        add_btn.pack(side=tk.LEFT)

        list_container = tk.Frame(self.todo_frame, bg=COLORS["panel"])
        list_container.pack(fill=tk.BOTH, expand=True, padx=8, pady=(0, 8))

        self.todo_canvas = tk.Canvas(list_container, bg=COLORS["panel"], highlightthickness=0)
        self.todo_scroll = ttk.Scrollbar(list_container, orient="vertical", command=self.todo_canvas.yview)
        self.todo_canvas.configure(yscrollcommand=self.todo_scroll.set)

        self.todo_list_frame = tk.Frame(self.todo_canvas, bg=COLORS["panel"])
        self.todo_list_window = self.todo_canvas.create_window(
            (0, 0), window=self.todo_list_frame, anchor="nw"
        )

        self.todo_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.todo_scroll.pack(side=tk.RIGHT, fill=tk.Y)

        self.todo_list_frame.bind("<Configure>", self.on_todo_list_configure)
        self.todo_canvas.bind("<Configure>", self.on_todo_canvas_configure)

    def build_history_panel(self) -> None:
        header = tk.Label(
            self.history_frame,
            text="Completed History",
            font=self.font_body,
            fg=COLORS["text"],
            bg=COLORS["panel"],
        )
        header.pack(anchor="w", padx=10, pady=(8, 4))

        list_container = tk.Frame(self.history_frame, bg=COLORS["panel"])
        list_container.pack(fill=tk.BOTH, expand=True, padx=8, pady=(0, 8))

        self.history_canvas = tk.Canvas(list_container, bg=COLORS["panel"], highlightthickness=0)
        self.history_scroll = ttk.Scrollbar(list_container, orient="vertical", command=self.history_canvas.yview)
        self.history_canvas.configure(yscrollcommand=self.history_scroll.set)

        self.history_list_frame = tk.Frame(self.history_canvas, bg=COLORS["panel"])
        self.history_list_window = self.history_canvas.create_window(
            (0, 0), window=self.history_list_frame, anchor="nw"
        )

        self.history_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.history_scroll.pack(side=tk.RIGHT, fill=tk.Y)

        self.history_list_frame.bind("<Configure>", self.on_history_list_configure)
        self.history_canvas.bind("<Configure>", self.on_history_canvas_configure)

    def build_xp_panel(self) -> None:
        self.xp_label = tk.Label(
            self.xp_frame,
            text="XP: 0 / 100",
            font=self.font_body,
            fg=COLORS["text"],
            bg=COLORS["panel"],
        )
        self.xp_label.pack(anchor="w", padx=10, pady=(8, 0))

        self.xp_bar_canvas = tk.Canvas(self.xp_frame, height=20, bg=COLORS["panel"], highlightthickness=0)
        self.xp_bar_canvas.pack(fill=tk.X, padx=10, pady=(4, 10))

    def on_resize(self, event: tk.Event) -> None:
        self.draw_background(event.width, event.height)
        padding = 16
        hud_width = 320
        hud_height = 80
        xp_height = 64
        left_width = max(360, int(event.width * 0.58))
        right_width = max(220, event.width - left_width - padding * 3)
        top_y = padding + hud_height + padding

        self.canvas.coords(self.hud_window, padding, padding)
        self.canvas.itemconfigure(self.hud_window, width=hud_width, height=hud_height)

        self.canvas.coords(self.todo_window, padding, top_y)
        self.canvas.itemconfigure(self.todo_window, width=left_width, height=event.height - top_y - xp_height - padding * 2)

        self.canvas.coords(self.history_window, padding * 2 + left_width, top_y)
        self.canvas.itemconfigure(self.history_window, width=right_width, height=event.height - top_y - xp_height - padding * 2)

        self.canvas.coords(self.xp_window, padding, event.height - xp_height - padding)
        self.canvas.itemconfigure(self.xp_window, width=event.width - padding * 2, height=xp_height)

    def draw_background(self, width: int, height: int) -> None:
        self.canvas.delete("bg")
        sky_height = int(height * 0.35)
        self.canvas.create_rectangle(0, 0, width, sky_height, fill=COLORS["sky_top"], outline="", tags="bg")
        self.canvas.create_rectangle(0, sky_height, width, sky_height + 20, fill=COLORS["sky_bottom"], outline="", tags="bg")

        sea_start = sky_height + 20
        band_height = 18
        y = sea_start
        toggle = True
        while y < height:
            color = COLORS["sea_light"] if toggle else COLORS["sea_dark"]
            self.canvas.create_rectangle(0, y, width, min(y + band_height, height), fill=color, outline="", tags="bg")
            toggle = not toggle
            y += band_height

        island_width = int(width * 0.45)
        island_height = int(height * 0.22)
        island_x0 = int(width * 0.28)
        island_y0 = int(height * 0.48)
        self.canvas.create_oval(
            island_x0,
            island_y0,
            island_x0 + island_width,
            island_y0 + island_height,
            fill=COLORS["island_sand"],
            outline="",
            tags="bg",
        )
        self.canvas.create_oval(
            island_x0 + 30,
            island_y0 + 12,
            island_x0 + island_width - 30,
            island_y0 + island_height - 18,
            fill=COLORS["island_grass"],
            outline="",
            tags="bg",
        )

        palm_x = island_x0 + int(island_width * 0.2)
        palm_y = island_y0 + int(island_height * 0.15)
        self.canvas.create_rectangle(palm_x, palm_y, palm_x + 6, palm_y + 40, fill="#8b5a2b", outline="", tags="bg")
        self.canvas.create_rectangle(palm_x - 14, palm_y - 6, palm_x + 20, palm_y + 4, fill="#4fa85b", outline="", tags="bg")

    def on_todo_list_configure(self, _event: tk.Event) -> None:
        self.todo_canvas.configure(scrollregion=self.todo_canvas.bbox("all"))

    def on_todo_canvas_configure(self, event: tk.Event) -> None:
        self.todo_canvas.itemconfigure(self.todo_list_window, width=event.width)

    def on_history_list_configure(self, _event: tk.Event) -> None:
        self.history_canvas.configure(scrollregion=self.history_canvas.bbox("all"))

    def on_history_canvas_configure(self, event: tk.Event) -> None:
        self.history_canvas.itemconfigure(self.history_list_window, width=event.width)

    def increment_weight(self, delta: int) -> None:
        current = self.new_weight_var.get()
        new_value = max(1, min(5, current + delta))
        self.new_weight_var.set(new_value)

    def add_task(self) -> None:
        text = self.new_task_text.get().strip()
        if not text:
            return
        weight = self.safe_weight(self.new_weight_var.get())
        task_id = uuid.uuid4().hex
        task = Task(id=task_id, text=text, weight=weight)
        self.tasks[task_id] = task
        self.new_task_text.delete(0, tk.END)
        self.new_weight_var.set(2)
        self.new_task_text.focus_set()
        self.refresh_task_list()
        self.save_data()

    def complete_task(self, task_id: str) -> None:
        task = self.tasks.pop(task_id, None)
        if not task:
            return
        task.completed = True
        task.completed_at = "now"
        self.history.insert(0, task)
        old_level = self.xp_total // XP_PER_LEVEL + 1
        self.xp_total += task.weight * XP_PER_WEIGHT
        new_level = self.xp_total // XP_PER_LEVEL + 1
        self.refresh_task_list()
        self.refresh_history_list()
        self.update_xp_bar()
        self.save_data()
        if new_level > old_level:
            self.show_level_up_animation(new_level)

    def delete_task(self, task_id: str) -> None:
        if task_id in self.tasks:
            self.tasks.pop(task_id)
            self.refresh_task_list()
            self.save_data()

    def update_task_text(self, task_id: str, text: str) -> None:
        if task_id in self.tasks:
            self.tasks[task_id].text = text.strip()
            self.save_data()

    def update_task_weight(self, task_id: str, weight: int) -> None:
        if task_id in self.tasks:
            self.tasks[task_id].weight = weight
            self.save_data()

    def refresh_task_list(self) -> None:
        for child in self.todo_list_frame.winfo_children():
            child.destroy()

        for task in self.tasks.values():
            row = tk.Frame(self.todo_list_frame, bg=COLORS["panel"], pady=4)
            row.pack(fill=tk.X, padx=6)

            entry = tk.Entry(row, font=self.font_body)
            entry.insert(0, task.text)
            entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 6))
            entry.bind(
                "<FocusOut>",
                lambda event, tid=task.id, widget=entry: self.update_task_text(tid, widget.get()),
            )

            weight_var = tk.IntVar(value=task.weight)
            weight_spin = tk.Spinbox(
                row,
                from_=1,
                to=5,
                width=3,
                textvariable=weight_var,
                font=self.font_body,
            )
            weight_spin.pack(side=tk.LEFT, padx=(0, 6))
            weight_var.trace_add(
                "write",
                lambda *_args, tid=task.id, var=weight_var: self.update_task_weight(
                    tid, self.safe_weight(var.get())
                ),
            )

            done_btn = tk.Button(
                row,
                text="Done",
                font=self.font_small,
                command=lambda tid=task.id: self.complete_task(tid),
                bg=COLORS["accent"],
                fg="#000000",
                activebackground=COLORS["accent_dark"],
                width=6,
            )
            done_btn.pack(side=tk.LEFT, padx=(0, 4))

            del_btn = tk.Button(
                row,
                text="X",
                font=self.font_small,
                command=lambda tid=task.id: self.delete_task(tid),
                bg=COLORS["panel_border"],
                fg=COLORS["text"],
                width=2,
            )
            del_btn.pack(side=tk.LEFT)

        if not self.tasks:
            empty = tk.Label(
                self.todo_list_frame,
                text="No active quests. Add one above.",
                font=self.font_small,
                fg=COLORS["muted"],
                bg=COLORS["panel"],
            )
            empty.pack(anchor="w", padx=10, pady=6)

    def refresh_history_list(self) -> None:
        for child in self.history_list_frame.winfo_children():
            child.destroy()

        for task in self.history:
            row = tk.Frame(self.history_list_frame, bg=COLORS["panel"], pady=4)
            row.pack(fill=tk.X, padx=6)
            label = tk.Label(
                row,
                text=f"✓ {task.text} (w:{task.weight})",
                font=self.font_strike,
                fg=COLORS["muted"],
                bg=COLORS["panel"],
            )
            label.pack(anchor="w")

        if not self.history:
            empty = tk.Label(
                self.history_list_frame,
                text="No completed quests yet.",
                font=self.font_small,
                fg=COLORS["muted"],
                bg=COLORS["panel"],
            )
            empty.pack(anchor="w", padx=10, pady=6)

    def update_xp_bar(self) -> None:
        level = self.xp_total // XP_PER_LEVEL + 1
        current_level_xp = self.xp_total % XP_PER_LEVEL
        self.level_label.configure(text=f"Level {level}")
        self.xp_label.configure(text=f"XP: {current_level_xp} / {XP_PER_LEVEL}")

        self.xp_bar_canvas.delete("bar")
        width = max(self.xp_bar_canvas.winfo_width() - 4, 10)
        fill_width = int(width * (current_level_xp / XP_PER_LEVEL))
        self.xp_bar_canvas.create_rectangle(2, 4, width + 2, 16, fill="#000000", outline="", tags="bar")
        self.xp_bar_canvas.create_rectangle(
            2, 4, fill_width + 2, 16, fill=COLORS["accent"], outline="", tags="bar"
        )

    def safe_weight(self, value: int) -> int:
        try:
            weight = int(value)
        except (TypeError, ValueError):
            return 1
        return max(1, min(5, weight))

    def load_data(self) -> None:
        if not os.path.exists(DATA_FILE):
            return
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as handle:
                payload = json.load(handle)
        except (OSError, json.JSONDecodeError):
            return

        self.xp_total = int(payload.get("xp", 0))
        for item in payload.get("tasks", []):
            task = Task(**item)
            if not task.completed:
                self.tasks[task.id] = task

        self.history = [Task(**item) for item in payload.get("history", [])]

    def save_data(self) -> None:
        payload = {
            "xp": self.xp_total,
            "tasks": [asdict(task) for task in self.tasks.values()],
            "history": [asdict(task) for task in self.history[:200]],
        }
        try:
            with open(DATA_FILE, "w", encoding="utf-8") as handle:
                json.dump(payload, handle, indent=2)
        except OSError:
            pass

    def show_level_up_animation(self, level: int) -> None:
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        center_x = width // 2
        center_y = height // 2

        # Create overlay that sits on top of everything
        self.overlay_frame = tk.Frame(self.root)
        self.overlay_frame.place(x=0, y=0, width=width, height=height)
        self.overlay_canvas = tk.Canvas(self.overlay_frame, bg=COLORS["sea_dark"], highlightthickness=0)
        self.overlay_canvas.pack(fill=tk.BOTH, expand=True)

        # Create semi-transparent overlay
        overlay = self.overlay_canvas.create_rectangle(
            0, 0, width, height,
            fill="#000000",
            stipple="gray50",
            tags="levelup"
        )

        # Create star burst effect
        star_positions = [
            (center_x - 100, center_y - 80),
            (center_x + 100, center_y - 80),
            (center_x - 120, center_y),
            (center_x + 120, center_y),
            (center_x - 100, center_y + 80),
            (center_x + 100, center_y + 80),
        ]
        for sx, sy in star_positions:
            self.overlay_canvas.create_text(
                sx, sy,
                text="★",
                font=tkfont.Font(family="Arial", size=24),
                fill=COLORS["accent"],
                tags="levelup"
            )

        # Create main level-up text with background
        bg_rect = self.overlay_canvas.create_rectangle(
            center_x - 150, center_y - 50,
            center_x + 150, center_y + 50,
            fill=COLORS["panel"],
            outline=COLORS["accent"],
            width=4,
            tags="levelup"
        )

        levelup_font = tkfont.Font(family="Lucida Console", size=32, weight="bold")
        shadow_id = self.overlay_canvas.create_text(
            center_x + 3,
            center_y + 3,
            text=f"LEVEL {level}!",
            font=levelup_font,
            fill="#000000",
            tags="levelup",
        )
        text_id = self.overlay_canvas.create_text(
            center_x,
            center_y,
            text=f"LEVEL {level}!",
            font=levelup_font,
            fill=COLORS["accent"],
            tags="levelup",
        )

        self.animate_level_up(center_x, center_y, 0)

    def animate_level_up(self, center_x: int, center_y: int, step: int) -> None:
        if step >= 60:
            if self.overlay_canvas:
                self.overlay_canvas.destroy()
                self.overlay_canvas = None
            if self.overlay_frame:
                self.overlay_frame.destroy()
                self.overlay_frame = None
            return

        if not self.overlay_canvas:
            return

        # Pulse effect - make it slightly bigger and smaller
        if step < 10:
            scale = 1.0 + (step / 10) * 0.15
        elif step < 20:
            scale = 1.15 - ((step - 10) / 10) * 0.1
        elif step < 30:
            scale = 1.05 + ((step - 20) / 10) * 0.05
        elif step < 40:
            scale = 1.1 - ((step - 30) / 10) * 0.05
        else:
            scale = 1.05

        # Move stars outward slightly
        if step < 30:
            star_items = [item for item in self.overlay_canvas.find_withtag("levelup") 
                         if self.overlay_canvas.type(item) == "text" and self.overlay_canvas.itemcget(item, "text") == "★"]
            for star in star_items:
                coords = self.overlay_canvas.coords(star)
                if coords:
                    x, y = coords[0], coords[1]
                    dx = (x - center_x) * 0.02
                    dy = (y - center_y) * 0.02
                    self.overlay_canvas.move(star, dx, dy)

        self.root.after(50, lambda: self.animate_level_up(center_x, center_y, step + 1))

    def on_close(self) -> None:
        self.save_data()
        self.root.destroy()


def main() -> None:
    root = tk.Tk()
    app = TodoApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
