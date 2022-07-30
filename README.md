# Aspinwall Launcher <a href="https://hosted.weblate.org/engage/aspinwall-ui/"><img src="https://hosted.weblate.org/widgets/aspinwall-ui/-/aspinwall-shell/svg-badge.svg" alt="Translation status" /></a>

Smart display-esque launcher for mobile Linux

![Launcher screenshot](docs/launcher-screenshot.png)

## About

The Aspinwall Launcher is a launcher for Linux devices. It shows the current time and date, as well as widgets selected by the user.

Widgets are written in Python and can be easily integrated with existing libraries.

## Installing

The project can be built and installed with Meson:

```shell
$ meson . build
$ meson compile -C build
$ sudo meson install -C build
```

For development purposes, the launcher can be started using the provided `./run` script.

Before you can use the `./run-*` scripts, you will need to install Meson.

## Requirements

### Runtime

- GTK 4.0 (>4.5.0 required for libadwaita 1.0.0)
- libadwaita >= 1.0.0
- GLib
- Python >= 3.6
- PyGObject

### Build

These are also needed if you're planning to use the provided run scripts.

- meson
- glib2-dev or equivalent (needed for `glib-compile-schemas`)
- desktop-file-utils (needed for `update-desktop-database`)

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md).

We use [Hosted Weblate](https://hosted.weblate.org/projects/aspinwall-ui/) to manage translations. Built-in widget translations are split to their own sub-components; the translations can be found in the [Aspinwall Launcher](https://hosted.weblate.org/projects/aspinwall-ui/aspinwall-launcher/) component.
