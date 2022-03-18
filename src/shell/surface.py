# coding: utf-8
"""
Abstraction code for shell elements.
"""
from gi.repository import Gtk, Gdk, GObject

class Surface(Gtk.Window):
	"""
	Generic class for shell elements.
	"""
	__gtype_name__ = 'ShellSurface'

	# Currently this is derived from Gtk.Window; the final goal is to have
	# something akin to Phosh's PhoshLayerSurface, but with support for
	# both X11 and Wayland, hopefully with as little breakage during the
	# transition as possible.

	def __init__(self, application,
			valign=Gtk.Align.START, halign=Gtk.Align.END,
			vexpand=False, hexpand=False, width=0, height=0):
		"""Initializes a shell surface."""
		super().__init__(application=application,
			resizable=False,
			decorated=False,
			deletable=False
		)

		self.show()

		# Set surface width/height
		monitor = Gdk.Display.get_default().get_monitor_at_surface(
			self.get_surface()
		)
		if hexpand is True:
			width = monitor.get_geometry().width
		if vexpand is True:
			height = monitor.get_geometry().height
		self.set_size_request(width, height)

		self.width = width
		self.height = height

		# TODO: Set surface alignment

	@GObject.Property(type=int, flags=GObject.ParamFlags.READABLE)
	def surface_width(self):
		"""
		Width of the surface.

		Should be used in derived objects instead of the monitor width, as
		this allows it to be easily changed for debugging purposes.
		"""
		return self.width

	@GObject.Property(type=int, flags=GObject.ParamFlags.READABLE)
	def surface_height(self):
		"""
		Height of the surface.

		Should be used in derived objects instead of the monitor height, as
		this allows it to be easily changed for debugging purposes.
		"""
		return self.height
