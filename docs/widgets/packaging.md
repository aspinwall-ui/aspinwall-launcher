# Packaging widgets

Widgets can be packaged to allow them to be installed by end users using the "Install widgets" button in the widget chooser.

A widget package is a gzipped .tar file (`.tar.gz` extension) containing the following:

- `metadata.json` - the widget's metadata in JSON format
- a folder named exactly like the widget's ID (case-sensitive). This contains the "precompiled" widget directory, exactly as it is copied onto the system.

The [example widget repository](https://github.com/aspinwall-ui/aspinwall-example-widget) contains a script named `package` that can generate this kind of package automatically.
