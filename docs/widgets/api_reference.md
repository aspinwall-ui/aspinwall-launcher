# Widget API reference

All widgets are derived from a central [`Widget`](https://github.com/aspinwall-ui/aspinwall-launcher/blob/develop/src/widgets/__init__.py#L12) class. This document describes the properties and functions available in this class.

For a more tutorial-esque approach to widgets, see [Creating a new widget](docs/widgets/creating_widgets.md).

## Properties

### Metadata

Widgets have a `metadata` property, which is a dictionary containing the following keys:

 * `id` (string) - the widget's ID.
 * `version` (string) - the widget's version.
 * `name` (string) - the widget's name
 * `icon` (string) - the widget's icon, as an icon name string
 * `description` (string) - the widget's description
 * `author` (string) - the name of the widget's author
 * `tags` (string) - the widget's tags, separated by commas
 * `url` (string) (optional) - an URL to the widget's repository.
 * `issue_tracker` (string) (optional) - an URL to the widget's issue tracker.

These keys are also exposed as GObject properties; the property names for them are the same as the key names, with two notable differences:

 * `icon` is exposed as `icon_name`
 * The `tags` GObject property returns a list with the tags pre-split, as opposed to the raw tags string.

### Informational properties

 * `has_config` (bool, default=False) - whether the widget uses GSettings configuration.
 * `has_settings_menu` (bool, default=False) - whether the widget has a settings menu.
 * `has_stylesheet` (bool, default=False) - whether the widget has stylesheets (`stylesheet/style.css`, `stylesheet/style-dark.css`, `stylesheet/style-hc.css`).
 * `has_gresource` (bool, default=False) - whether the widget uses a GResource file.
 * `no_padding` (bool, default=False) - if True, this removes the 10px padding that is added to widgets by default (to wrap nicely around the rounded corners).
 * `hide_edit_button` (bool, default=False) - whether to hide the edit button that appears when hovering over the widget with the mouse cursor. Useful for widgets that need the space in the corners for other buttons/content.
 * `schema_base_path` (string, default=None) - the GSettings schema base path. Set automatically from the widget's ID if this variable is unset.
 * `widget_path` (string, **set by initialization function**) - the path to the widget's files.
 * `instance` (string, **set by initialization function**) - the widget's unique instance ID (not to be confused with the widget's ID). The instance ID is used to differentiate instances of the same widget, and are used to keep configs separate between widgets.

### Other API properties

 * `_container` - an AdwBin that contains the widget's content. Set this with `Widget.set_child()`.
 * `_settings_container` - an AdwBin that contains the widget's content. Set this with `Widget.set_settings_child()`.
 * `config` - a GSettings object. Used for storing/accessing the widget's configuration, if enabled. **This is undefined if `has_config` is set to false**; using `self.config` when it is not set is considered a programming error.
 * `gresource` - a GResource object. **This is undefined if `has_gresource` is set to false**.
 * `settings_toggled` (**GObject property**) - whether or not the widget settings are currently being displayed. **This is undefined if `has_settings_menu is set to false**.

## Functions

 * `set_child(self, widget)` - Sets the container of the widget.
 * `set_settings_child(self, widget)` - Sets the settings menu container of the widget. Only works if `has_settings_menu` is True.
 * `join_self_with_data_path(self, *args)` - Joins path relative to widget data directory. Arguments are provided as arguments for `os.path.join` (so, each argument is a separate subdirectory/file).
 * `refresh(self)` - Refreshes the widget. **Defined by the widgets**, by default does nothing.
 * `load_stylesheet_from_file(self, path)` - Loads a stylesheet from the given path.
 * `load_stylesheet_from_string(self, string)` - Loads a stylesheet from the given string.
