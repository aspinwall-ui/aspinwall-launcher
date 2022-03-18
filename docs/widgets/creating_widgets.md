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
 - `tags` - a string containing a list of tags, separated by commas
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
		'tags': 'hello world,example',
		'thumbnail': []
	}

	def __init__(self, instance):
		# FIXME: Add content here
		super().__init__(instance)
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

## Installing the widget

The default local folder for widgets is `~/.local/share/aspinwall/widgets`.

To prepare a widget for installation:

  - Create a folder with the widget's ID in lowercase as the name
  - Place your widget's `.py` file into the folder
  - If your widgets have schemas, place the compiled `gschemas.compiled` file into a subfolder named `schemas`.

To install the widget, move it to the widget folder, whether it's the local one or the system one.

## Testing the widget

You can now run the launcher (if you don't have it installed, use the provided `run` script) and add your widget to the launcher. If all goes well, you should now have a working widget!

## Adding more advanced features

So far, we have only covered the basics of adding/removing content to a widget. To access the full potential of widgets, there are multiple convenience features built into the widget API.

### Widget configuration

Widgets can have their own configuration. Internally, this uses [GSettings](https://docs.gtk.org/gio/class.Settings.html); a `Gio.Settings` object is automatically created by the API and stored in `self.config`.

The config value behaves like a regular dict - `self.config['key']` gets a key, and `self.config['key'] = value` sets it. The values set in the widget are specific for each instance of a widget - every instance of a widget has a separate config. This is all handled by the widget API - no user interaction is needed.

As the configuration uses `Gio.Settings` internally, widgets that use the config **must provide their own schemas**. The schema file for the widget must be placed in the `schemas` subfolder. See [HowDoI/GSettings](https://wiki.gnome.org/HowDoI/GSettings) for information on creating schema files, but take note of some Aspinwall-specific things:

* **Do not define a path.** Usually in schema files the `<schema ...>` tag has a `path` attribute. We must not set this attribute, as we use relocatable schemas - the path is automatically created by the widget API. (The base path can be overwritten with the `self.schema_base_path` variable - most users will not need to do this.) 
* **The schema ID must exactly match the widget's ID.** Note that this is *case-sensitive*.
* **The schema's XML file must be placed in the `schemas` subdirectory in your widget directory.** Additionally, widgets that are shipped are expected to compile these schemas; see the `meson.build` files in the widget directories for a way to do this through Meson.

Additionally, widgets that are planning to use the config variable **must** set `self.has_config` to True (usually by placing `has_config = True` above your init function, below the metadata).

If your widget has no configuration options, you don't need to set the `has_config` value; it is set to False by default.

### Settings menu

In some cases, a widget might need to have its own settings options. The widget API allows for the addition of a settings menu, which is created by the widget and can be opened through the settings button in the widget header.

To add a settings menu, set `self.has_settings_menu` to True and set `self.settings_menu` to the widget to use as the settings container.

Note that in most cases, you will want to wrap your settings container widget in a `GtkScrolledWindow`. Make sure that the `GtkScrolledWindow` has the `vexpand` attribute set to `True`.

Adding a settings menu is completely optional, and you don't need to add a settings menu if you just want to utilize the configuration backend.

### Refreshing widget content

Widget classes can have a `refresh` function, which will automatically run in the background at a certain time, and/or whenever the launcher is started (this depends on user settings).

A refresh button will appear in the widget's header if this function is defined, which will allow the user to refresh the widget at any given moment.

Any commands that request data should be placed in this function. However, widgets that need to request data more often or need to process multiple events at once (for example, progress bars or buttons) can add background threads of their own.

Using this function is not required, it is merely a suggestion to speed up development and allow for more fine-tuned power saving measures.

### Styling widgets

Widgets are automatically set up with a `GtkCssProvider`, which is stored in the `self.css_provider` variable.

CSS properties can be loaded from a file (here we use `stylesheet.css` in the widget folder):
```python
	self.css_provider.load_from_path(self.join_with_data_path('stylesheet.css'))
```
