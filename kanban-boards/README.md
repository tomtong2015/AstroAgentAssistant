# Kanban Board Archives

Exported kanban boards from this Hermes deployment, ready to be restored into another Hermes Agent instance.

## Available boards

| Board | Name | Tasks | Status |
|---|---|---|---|
| `drp-paper` | DRP White Paper (EPJ) | 7 | All done ✅ |

## How to restore a board into a new Hermes profile

### Prerequisites
- Hermes Agent installed and configured with a `kanban` directory at `~/.hermes/kanban/`

### Steps

1. **Clone the board files** into the new Hermes profile's kanban directory:

```bash
# Create the kanban/boards directory if it doesn't exist
mkdir -p ~/.hermes/kanban/boards

# Copy the board you want to restore
cp -r /path/to/this/repo/kanban-boards/drp-paper ~/.hermes/kanban/boards/

# Remove the lock files (they are process-specific)
rm -f ~/.hermes/kanban/boards/drp-paper/kanban.db.dispatch.lock
rm -f ~/.hermes/kanban/boards/drp-paper/kanban.db.init.lock
```

2. **Switch to the restored board** in your new Hermes profile:

```bash
hermes kanban boards switch drp-paper
```

3. **Verify the board loaded correctly**:

```bash
hermes kanban list
hermes kanban stats
```

### Notes
- Lock files (`kanban.db.dispatch.lock`, `kanban.db.init.lock`) are process-specific and should be removed before restoring.
- The board slug (`drp-paper`) is preserved — it matches the directory name and `board.json`.
- Task IDs, statuses, and comments are fully preserved in the SQLite database.
