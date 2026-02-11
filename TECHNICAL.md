# Technical Documentation

## Architecture Overview

Island Todo Quest is built as a single-file Python application using Tkinter for the GUI. The application follows an object-oriented design with a main `TodoApp` class managing all UI components, state, and interactions.

## Code Structure

### Main Components

#### `TodoApp` Class
The central application class that manages:
- Window initialization and layout
- UI panel creation and management
- Task lifecycle (add, complete, delete, edit)
- XP tracking and level progression
- Data persistence
- Animation system

### Data Models

#### `Task` Dataclass
```python
@dataclass
class Task:
    id: str              # Unique identifier (UUID)
    text: str            # Task description
    weight: int          # Task difficulty/importance (1-5)
    completed: bool      # Completion status
    completed_at: str    # Timestamp (currently "now")
```

### UI Layout

The application uses a canvas-based layout with positioned window frames:

1. **Background Canvas** (`self.canvas`)
   - Draws the 8-bit island scene (sky gradient, ocean bands, island, palm tree)
   - Hosts all UI panels as canvas windows
   - Handles resize events and redraws background

2. **HUD Frame** (`self.hud_frame`)
   - Top-left panel showing title and current level
   - Fixed width (320px), positioned at top-left

3. **Todo Frame** (`self.todo_frame`)
   - Main quest panel with scrollable list
   - Input field for new tasks
   - Weight spinner (1-5 range)
   - Each task row contains: text entry, weight spinner, Done button, X (delete) button

4. **History Frame** (`self.history_frame`)
   - Right-side panel showing completed tasks
   - Scrollable list with strikethrough text
   - Shows checkmark (✓) and task weight

5. **XP Frame** (`self.xp_frame`)
   - Bottom panel spanning full width
   - Text label showing current XP / next level XP
   - Animated progress bar using canvas rectangles

6. **Overlay System** (`self.overlay_frame`, `self.overlay_canvas`)
   - Created dynamically when leveling up
   - Sits above all other UI elements
   - Destroyed after animation completes

### Key Methods

#### Layout & Rendering

- **`on_resize(event)`** – Repositions all UI panels when window resizes
- **`draw_background(width, height)`** – Renders the island scene with layered ocean effect
- **`update_xp_bar()`** – Recalculates and redraws the XP progress bar

#### Task Management

- **`add_task()`** – Creates new task from input fields, generates UUID, saves data
- **`complete_task(task_id)`** – Moves task to history, awards XP, triggers level-up check
- **`delete_task(task_id)`** – Removes task from active list
- **`update_task_text(task_id, text)`** – Updates task description on blur
- **`update_task_weight(task_id, weight)`** – Updates task weight when spinner changes

#### UI Refresh

- **`refresh_task_list()`** – Rebuilds active quest panel with current tasks
- **`refresh_history_list()`** – Rebuilds completed history panel
- Both methods destroy old widgets and recreate from current state

#### Animation System

- **`show_level_up_animation(level)`** – Creates overlay with:
  - Semi-transparent dark background (stippled rectangle)
  - 6 star symbols (★) positioned around center
  - Bordered panel with "LEVEL X!" text
  - Shadow effect on text

- **`animate_level_up(center_x, center_y, step)`** – 60-frame animation loop:
  - Frames 0-10: Scale up (pulse effect)
  - Frames 10-20: Scale down slightly
  - Frames 20-40: Secondary pulse
  - Frames 0-30: Stars drift outward
  - Frame 60: Destroy overlay

#### Data Persistence

- **`load_data()`** – Reads `todo_data.json` on startup
  - Restores XP total
  - Reconstructs active tasks (incomplete only)
  - Loads history array

- **`save_data()`** – Writes to `todo_data.json` after any change
  - Stores XP total
  - Serializes active tasks
  - Keeps last 200 completed tasks in history

### Game Mechanics

#### XP System

```python
XP_PER_WEIGHT = 10    # Each weight point = 10 XP
XP_PER_LEVEL = 100    # Level up every 100 XP
```

- **Task XP Calculation:** `task.weight × 10`
- **Level Calculation:** `(total_xp // 100) + 1`
- **Current Level XP:** `total_xp % 100`

Example progression:
- Weight 1 task = 10 XP
- Weight 5 task = 50 XP
- Level 1 → Level 2 = 100 XP (10 weight-1 tasks, or 2 weight-5 tasks)

#### Weight System

Tasks can be assigned weights 1-5:
- **1:** Simple, quick tasks
- **2:** Default weight for new tasks
- **3-4:** Medium effort tasks
- **5:** Major tasks or milestones

### Color Palette

The 8-bit island aesthetic uses a carefully chosen color scheme:

```python
COLORS = {
    "sky_top": "#9ed8ff",        # Light blue gradient top
    "sky_bottom": "#6fb7f1",     # Medium blue gradient bottom
    "sea_dark": "#1f5d9b",       # Dark ocean band
    "sea_light": "#2b78c7",      # Light ocean band (alternating)
    "island_sand": "#f1d48a",    # Beige sand outline
    "island_grass": "#5dbb63",   # Green island center
    "panel": "#1a2a3a",          # Dark blue-gray UI panels
    "panel_border": "#4e6a7d",   # Lighter border for panels
    "text": "#e7f6ff",           # Off-white text
    "muted": "#b8d0e0",          # Gray text for history
    "accent": "#ffcc4d",         # Yellow for highlights/XP
    "accent_dark": "#c89b2e",    # Darker yellow for hover states
}
```

### Keyboard Bindings

```python
# Task input field
self.new_task_text.bind("<Return>", lambda e: self.add_task())
self.new_task_text.bind("<Up>", lambda e: self.increment_weight(1))
self.new_task_text.bind("<Down>", lambda e: self.increment_weight(-1))

# Weight spinner
self.new_weight_spin.bind("<Return>", lambda e: self.add_task())
```

### Background Scene Construction

The island scene is drawn in layers from back to front:

1. **Sky Gradient** (top 35% of canvas)
   - Solid top section with `sky_top` color
   - 20px transition band with `sky_bottom` color

2. **Ocean Bands** (remaining 65%)
   - Alternating 18px horizontal bands
   - Colors alternate between `sea_dark` and `sea_light`
   - Creates wave-like striped effect

3. **Island** (centered in ocean area)
   - Outer oval with `island_sand` color (45% width, 22% height)
   - Inner oval with `island_grass` color (slightly smaller)

4. **Palm Tree** (left side of island)
   - 6px wide brown rectangle for trunk
   - Green rectangle for fronds

### Scrollable Lists

Both the todo and history panels use a canvas-scrollbar pattern:

```python
# Container with scrollbar
list_container = tk.Frame(parent)
canvas = tk.Canvas(list_container)
scrollbar = ttk.Scrollbar(list_container, command=canvas.yview)
canvas.configure(yscrollcommand=scrollbar.set)

# Inner frame that holds actual content
inner_frame = tk.Frame(canvas)
canvas.create_window((0, 0), window=inner_frame, anchor="nw")

# Update scroll region when content changes
inner_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
```

### Safe Weight Handling

```python
def safe_weight(self, value: int) -> int:
    try:
        weight = int(value)
    except (TypeError, ValueError):
        return 1
    return max(1, min(5, weight))
```

Ensures weights are always integers between 1-5, defaulting to 1 if invalid.

## Dependencies

### Built-in Python Modules
- `tkinter` – GUI framework
- `tkinter.ttk` – Themed widgets (scrollbars)
- `tkinter.font` – Font management
- `dataclasses` – Task data structure
- `json` – Data persistence
- `os` – File operations
- `uuid` – Unique task IDs
- `typing` – Type hints

### External Dependencies (for building executable)
- `pyinstaller` – Converts Python script to standalone `.exe`

## Building for Distribution

### PyInstaller Command
```bash
pyinstaller --onefile --windowed --name "Island Todo Quest" main.py
```

**Flags:**
- `--onefile` – Bundle everything into a single executable
- `--windowed` – No console window (GUI only)
- `--name` – Custom executable name (with spaces)

### Output Structure
```
dist/
  Island Todo Quest.exe    # Standalone executable
build/                     # Temporary build files (can be deleted)
Island Todo Quest.spec     # PyInstaller configuration
```

## Data File Format

`todo_data.json` structure:

```json
{
  "xp": 250,
  "tasks": [
    {
      "id": "a1b2c3d4...",
      "text": "Complete project documentation",
      "weight": 4,
      "completed": false,
      "completed_at": null
    }
  ],
  "history": [
    {
      "id": "e5f6g7h8...",
      "text": "Review pull request",
      "weight": 2,
      "completed": true,
      "completed_at": "now"
    }
  ]
}
```

**Notes:**
- History is capped at 200 items (oldest discarded)
- File is created in the same directory as the executable
- Corrupted files are silently ignored (fresh start)

## Performance Considerations

- **Background redraw:** Only happens on window resize
- **Task list refresh:** Destroys and recreates widgets (simple but effective for small lists)
- **Animation:** 50ms frame time (20 FPS) for smooth appearance
- **Auto-save:** Writes JSON on every change (acceptable for typical usage)

## Future Enhancement Ideas

- Custom task icons or categories
- Sound effects on completion/level-up
- Daily/weekly statistics dashboard
- Export completed tasks to CSV
- Cloud sync support
- Custom XP/level formulas
- Achievement badges
- Task scheduling/reminders
- Drag-to-reorder tasks
- Custom island themes
- Multiple quest boards (work/personal/etc)

## Known Limitations

- No undo functionality
- History is display-only (cannot uncomplete tasks)
- No task prioritization beyond weight
- Single-user, single-instance (no multi-user support)
- No task search or filtering
- Window must be manually resized (no fullscreen mode)
- `completed_at` timestamp uses placeholder "now" instead of actual datetime

## Development Notes

The application was designed with simplicity in mind:
- Single-file architecture for easy distribution
- No external dependencies for runtime
- Uses built-in Tkinter for maximum compatibility
- JSON for human-readable data storage
- Defensive error handling for file operations
