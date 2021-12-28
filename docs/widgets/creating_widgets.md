# Creating a new widget

This document serves as a tutorial for creating a new widget, as well as a reference for working with the Widget base class.

## What is a widget?

In purely technical terms, a **widget** is a simple box containing a small, one-window GTK application.

In Aspinwall, widgets are fairly powerful - they're written in Python, and can run any Python code. As such, they are very versatile and can integrate with anything that has a Python library.

Thus, writing a widget involves writing a regular GTK app in Python - just on a much smaller scale, and with much less setup needed.

### Anatomy of a widget

Technically, a widget is just a `GtkBox`, and the `widgets.Widget` class is actually derived from the `GtkBox` class. 

When displayed in the launcher, widgets are prepended with a **header**; this contains the title and icon of the widget, as provided in the `title` and `icon` variables in the widget class.

***Note:** The title and icon cannot be changed while the widget is running.*

## Creating the widget class

First, begin by creating the widget file. You can use our simple [widget template](TODO) to get an initial file layout.

Then, add the widget class to your newly created file:

```python
from aspinwall.launcher.widgets import Widget
from gi.repository import Gtk

class MyWidget(Widget):
	metadata = {
		'name': 'My Widget',
		'description': 'My first widget',
		'tags': ['hello world'],
		'image_urls': []
	}

	title = 'My Widget'
	icon = 'preferences-system-symbolic'

	def __init__(self):
		# FIXME
		raise NotImplementedError
```

## Creating the widget content

Widgets are basically small GTK apps - thus, creating the content is roughly equivalent to writing a regular pygobject app, just with the `Widget` object instead of a separate `Gtk.Window`.

The widget itself is a `GtkBox`, so GTK elements can be added to the widget with:

```python
	self.add(element)
```

The code used for widget creation must be added to the `__init__()` function of the widget class.

## Refreshing widget content

Widget classes can have a `on_widget_refresh` function, which will automatically run in the background at a certain time, and/or whenever the launcher is started (this depends on user settings).

A refresh button will appear in the widget's header if this function is defined, which will allow the user to refresh the widget at any given moment.

Any commands that request data should be placed in this function. However, widgets that need to request data more often or need to process multiple events at once (for example, progress bars or buttons) can add background threads of their own.

Using this function is not required, it is merely a suggestion to speed up development and allow for more fine-tuned power saving measures.
