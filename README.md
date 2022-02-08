# Aspinwall

Linux tablet shell that turns your device into a smart hub when not in use

## About

Aspinwall is a Linux interface for tablets and touchscreen devices. It offers:

- A clean, focused launcher with a widget view - reminiscent of smart hub devices
- *(TODO)* Multitasking features, such as a dedicated app list and easy window control
- *(TODO)* Some level of convergence - the shell works on both vertical (portrait) and horizontal (landscape) displays, and the launcher can be set to display on a separate screen by default
- *(TODO)* A widget API for creating your own widgets
- *(TODO)* Integration with Mycroft

## Installing

The project can be built and installed with Meson:

```shell
$ meson . build
$ meson compile -C build
$ sudo meson install -C build
```

For development purposes, the launcher can be started using the provided `./run` script, which will automatically launch the GTK4 debugger.

Before you can use the `./run` script, you will need to install Meson.

### Requirements

- GTK 4.0 (>4.5.0 required for libadwaita 1.0.0)
- libadwaita >= 1.0.0
- GLib
- Python >= 3.6
- PyGObject

## Contributing

The project is still in early development; we'd recommend holding off from contributing for the next month or so, until the basic features are fully implemented.

We plan to add translations for Aspinwall projects, which will most likely be hosted on Weblate; however, this has not been set up yet.

The current TODO list for the shell can be found [here](https://github.com/aspinwall-ui/aspinwall/issues/1).

## FAQ

### **Q:** Where does the name come from?

**A**: The name *Aspinwall* is a reference to the location of [Henryk Sienkiewicz](https://en.wikipedia.org/wiki/Henryk_Sienkiewicz)'s novel, *The Lighthouse Keeper*. There's no real reason for why it was picked; it was chosen primarily for aesthetic purposes.

### **Q:** Does Aspinwall run on Android?

**A:** No. Aspinwall is a Linux shell, and there are no plans to release an Android port of any of the shell's elements (besides, there is no Android port of GTK to my knowledge).

With that being said, we encourage using Aspinwall on any old Android tablets you may have; give [postmarketOS](https://postmarketos.org) a try. Aspinwall is being developed with the limitations of downstream kernels in mind, so it should work relatively well on older devices not running a (close to) mainline kernel.

*Developer's note: Aspinwall is planned to be packaged for postmarketOS, however it is currently available as the project is still in very early development. Also, we are in no way affiliated with postmarketOS.*

### **Q:** Does Aspinwall run on Windows/Mac/any other platform supported by GTK4?

**A:** The launcher? Sure, but we won't provide any support for these kinds of setups (in fact, this wasn't even tested). The shell? Not so much.

### **Q:** Is Aspinwall a GNOME project?

**A:** Aspinwall attempts to follow some design philosophies from Phosh and GNOME, but is (currently) not affiliated with either of the two.
