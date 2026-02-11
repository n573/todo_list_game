# Island Todo Quest

## Original Vision

> I want a desktop application, made to run on Windows 10 and Windows 11.
> It should have the appearance of a game like the old 8-bit island games. 
> The main goal of this application is to motivate me to complete items on my todo list. 
> There should be an XP (experience) bar at the bottom of the window; I gain XP by checking items off the list. The amount of XP is determined by a weight assigned to the task when it is first entered into the list. 
> The list must be editable. Plain text is fine as long as each item is in its own distinct text box. 
> Check marks should appear over completed tasks; consider having a "history" of completed tasks marked with check marks and strikethrough.

## Description

**Island Todo Quest** is a gamified todo list application built with Python and Tkinter. It transforms your daily tasks into quests on a tropical island, complete with an XP system, level progression, and animated celebrations when you level up.

### Features

- **8-bit Island Aesthetic** – Pixel-style graphics with a layered ocean and island background
- **Weighted Task System** – Assign weights (1-5) to tasks; higher weights reward more XP
- **XP & Leveling** – Earn 10 XP per weight point; level up every 100 XP with animated celebration
- **Editable Quest List** – Each task has its own text field and weight spinner
- **Completed History** – View past completed tasks with checkmarks (✓) and strikethrough
- **Keyboard Shortcuts**:
  - `Enter` – Add new task
  - `Up/Down arrows` – Adjust task weight while typing
- **Auto-save** – All tasks and XP progress saved to `todo_data.json`
- **Level-up Animation** – Star burst effect with centered popup when you reach a new level

### Technology Stack

- **Language:** Python 3
- **GUI Framework:** Tkinter (built-in, no external dependencies)
- **Data Storage:** JSON file (`todo_data.json`)
- **Platform:** Windows 10/11 desktop

### Screenshots

The app features a three-panel layout:
- **Top-left:** Title and current level display
- **Center-left:** Active quests with editable text, weight control, and action buttons
- **Right:** Completed history with strikethrough formatting
- **Bottom:** XP progress bar showing current level progress

## Quick Start

### Running from Source

```powershell
python main.py
```

### Building an Executable

Run the build script to create a standalone `.exe`:

```powershell
.\build_exe.bat
```

The executable will be created in the `dist` folder and can be run without Python installed.

## Documentation

For detailed technical documentation, code architecture, and implementation details, see [TECHNICAL.md](TECHNICAL.md).

## Files

- `main.py` – Main application code
- `todo_data.json` – Auto-generated data file (tasks, XP, history)
- `build_exe.bat` – Script to build Windows executable
- `instructions.md` – Original design specifications

## License

This is a personal productivity tool. Feel free to modify and use as needed.
