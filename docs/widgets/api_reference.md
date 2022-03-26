# Widget API reference

All widgets are derived from a central [`Widget`](https://github.com/aspinwall-ui/aspinwall/blob/develop/src/widgets/__init__.py#L11) class. This document describes the properties and functions available in this class.

For a more tutorial-esque approach to widgets, see [Creating a new widget](docs/widgets/creating_widgets.md).

## Properties

### Metadata

Widgets have a `metadata` property, which is a dictionary containing the following keys:

 * `id` (string) - the widget's ID.
 * `name` (string) - the widget's name
 * `icon` (string) - the widget's icon, as an icon name string
 * `description` (string) - the widget's description
 * `tags` (string) - the widget's tags, separated by commas

These keys are also exposed as GObject properties; the property names for them are the same as the key names, with two notable differences:

 * `icon` is exposed as `icon_name`
 * The `tags` GObject property returns a list with the tags pre-split, as opposed to the raw tags string.

### Informational properties

 * `has_config` (bool, default=False) - whether the widget uses GSettings configuration.
 * `has_settings_menu` (bool, default=False) - whether the widget has a settings menu.
 * `schema_base_path` (string, default=None) - the GSettings schema base path. Set automatically from the widget's ID if this variable is unset.
 * `widget_path` (string, **set by initialization function**) - the path to the widget's files.
 * `instance` (string, **set by initialization function**) - the widget's unique instance ID (not to be confused with the widget's ID). The instance ID is used to differentiate instances of the same widget, and are used to keep configs separate between widgets.

### Other API properties

 * `content` - the widget's content. This is an empty GtkBox by default.
 * `css_provider` - a GtkCssProvider. Can be used to style the widget.
 * `config` - a GSettings object. Used for storing/accessing the widget's configuration, if enabled. **This is undefined if `has_config` is set to false**; using `self.config` when it is not set is considered a programming error.

## Functions

 * `join_self_with_data_path(self, *args)` - Joins path relative to widget data directory. Arguments are provided as arguments for `os.path.join` (so, each argument is a separate subdirectory/file).
 * `refresh(self)` - Refreshes the widget. **Defined by the widgets**, by default does nothing.
