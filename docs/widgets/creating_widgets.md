# Creating a new widget

This document serves as a tutorial for creating a new widget, as well as a reference for working with the Widget base class.

## What is a widget?

In purely technical terms, a **widget** is a simple box containing a small, one-window GTK application.

In Aspinwall, widgets are fairly powerful - they're written in Python, and can run any Python code. As such, they are very versatile and can integrate with anything that has a Python library.

Thus, writing a widget involves writing a regular GTK app in Python - just on a much smaller scale, and with much less setup needed.

### Anatomy of a widget

Every widget inherits from the `Widget` class, as defined in `aspinwall.widgets.Widget`. This class contains the information about the widget.

A widget's content is provided through the `content` variable, and it contains a GTK widget (usually a `GtkBox`, `GtkGrid` or other type of container). Information about the widget is stored in the `metadata` variable, which is a dict. It contains the following values:

 - `name` - the widget's name
 - `icon` - string containing the icon name to use for the widget
 - `description` - the widget's description (shown in the widget chooser)
 - `tags` - a list of tags
 - `thumbnail` - an url to a screenshot of the widget

When displayed in the launcher, the widget is wrapped in a `LauncherWidget` object and given a `LauncherWidgetHeader`; this header displays the widget's name and icon, and provides buttons for removing the widget from the launcher and accessing its settings.

***Note:** The metadata (including the name and icon) cannot be changed while the widget is running.*

## Creating the widget class

First, begin by creating the widget file. You can use our simple [widget template](TODO) to get an initial file layout.

Then, add the widget class to your newly created file:

```python
from aspinwall.widgets import Widget
from gi.repository import Gtk

class MyWidget(Widget):
	metadata = {
		'name': 'My Widget',
		'icon': 'preferences-system-symbolic',
		'description': 'My first widget',
		'tags': ['hello world'],
		'thumbnail': []
	}

	def __init__(self):
		# FIXME
		raise NotImplementedError
```

## Creating the widget content

Widgets are basically small GTK apps - thus, creating the content is roughly equivalent to writing a regular pygobject app, just with the `Widget` object instead of a separate `Gtk.Window`.

The widget's content is stored in the `content` variable. By default, this is initialized with an empty `GtkBox`; as such, items can be added with:

```python
	self.content.append(element)
```

However, the `content` variable can be overwritten with a custom container, be it a `GtkBox` or a different element entirely:

```python
	self.content = Gtk.Box(hexpand=True)
```

The code used for widget creation must be added to the `__init__()` function of the widget class.

## Widget configuration

Widgets use [GSettings](https://docs.gtk.org/gio/class.Settings.html) for storing data, and are expected to ship pre-compiled files. A `Gio.Settings` object is provided in the `config` variable on the object, and can be interacted with like a regular dict (`config['key']` gets a key, `config['key'] = value` sets it).

Loading/saving is handled by the launcher.

If you're planning to use the `config` variable, you must set the `has_config` value to True.

If your widget has no configuration options, don't set the `has_config` value; it is set to False by default.

## Installing the widget

The default local folder for widgets is `~/.local/share/aspinwall/widgets`.

To prepare a widget for installation:

  - Create a folder with the widget's ID in lowercase as the name
  - Place your widget's `.py` file into the folder
  - If your widgets have schemas, place the compiled `gschemas.compiled` file into a subfolder named `schemas`.

To install the widget, move it to the widget folder, whether it's the local one or the system one.

## Refreshing widget content

Widget classes can have a `refresh` function, which will automatically run in the background at a certain time, and/or whenever the launcher is started (this depends on user settings).

A refresh button will appear in the widget's header if this function is defined, which will allow the user to refresh the widget at any given moment.

Any commands that request data should be placed in this function. However, widgets that need to request data more often or need to process multiple events at once (for example, progress bars or buttons) can add background threads of their own.

Using this function is not required, it is merely a suggestion to speed up development and allow for more fine-tuned power saving measures.
