# Widget loading mechanism

Widgets are stored in their own directories, which contain their .py files, as well as any other bundled files (translations, settings schemas, etc.). These directories are stored in multiple locations:

- `$XDG_DATA_HOME/aspinwall/widgets` (usually this is `~/.local/share/aspinwall/widgets`)
- `/usr/share/aspinwall/widgets`
- ...and any other directories under `$XDG_DATA_DIRS`, in the `/aspinwall/widgets` subdirectory, assuming said subdirectory exists.

> **Relevant file**: see `src/widgets/loader.py`.

## Loading order

Widgets are first loaded from the user's local folder, then from `XDG_DATA_DIRS` in the order in which they are stored in said variable.

If a widget in a directory that's loaded later has the same ID as a widget in a directory that's loaded earlier, **the widget that was loaded earlier takes precedence**. Any further widgets with the same ID **will be ignored**.

This can be used to make personal modifications to widgets; an user can copy the widget to their local profile and modify it as needed - Aspinwall will simply load the new widget.

## Widget storage in configuration

In the launcher configuration, loaded widgets are stored in the `org.dithernet.aspinwall.launcher.widgets` GSettings property. This property is an array of tuples that contain the widget ID and its instance ID.

The instance ID is unique to each instance of a widget and is used to identify it. This is usually used to keep separate configuration options for each instance of a widget.

The widgetbox in the launcher uses this settings property to load the widgets as needed.

> **Relevant function**: see `WidgetBox.load_widgets()` in `src/launcher/launcher_boxes.py`.
