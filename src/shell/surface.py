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
			vexpand=False, hexpand=False, width=0, height=0,
			visible=True):
		"""Initializes a shell surface."""
		super().__init__(application=application,
			resizable=False,
			decorated=False,
			deletable=False,
			visible=visible
		)

		self._hexpand = hexpand
		self._vexpand = vexpand

		self.show()

		# Set surface width/height
		monitor = Gdk.Display.get_default().get_monitor_at_surface(
			self.get_surface()
		)
		self._monitor_width = monitor.get_geometry().width
		self._monitor_height = monitor.get_geometry().height

		monitor.connect('notify::geometry', self.update_size)

		if hexpand is True:
			width = self._monitor_width
		if vexpand is True:
			height = self._monitor_height
		self.set_size_request(width, height)

		self.width = width
		self.height = height

		if not visible:
			self.set_visible(False)
			self.hide()

		# TODO: Set surface alignment

	def update_size(self):
		"""Updates the size request of the surface based on its variables."""
		self.notify('surface-width')
		self.notify('surface-height')

		monitor = Gdk.Display.get_default().get_monitor_at_surface(
			self.get_surface()
		)
		self._monitor_width = monitor.get_geometry().width
		self._monitor_height = monitor.get_geometry().height

		if self.hexpand is True:
			self.width = self._monitor_width
		if self.vexpand is True:
			self.height = self._monitor_height

		self.set_size_request(self.width, self.height)

	@GObject.Property(type=int, flags=GObject.ParamFlags.READABLE)
	def surface_width(self):
		"""
		Width of the surface.

		Should be used in derived objects instead of the monitor width, as
		this allows it to be easily changed for debugging purposes.
		"""
		return self.width

	def set_width(self, value):
		"""Sets the width of the surface."""
		self.width = value
		self.update_size()

	@GObject.Property(type=int, flags=GObject.ParamFlags.READABLE)
	def surface_height(self):
		"""
		Height of the surface.

		Should be used in derived objects instead of the monitor height, as
		this allows it to be easily changed for debugging purposes.
		"""
		return self.height

	def set_height(self, value):
		"""Sets the height of the surface."""
		self.height = value
		self.update_size()

	@GObject.Property(type=int, flags=GObject.ParamFlags.READABLE)
	def monitor_width(self):
		"""
		Width of the monitor.
		"""
		return self._monitor_width

	@GObject.Property(type=int, flags=GObject.ParamFlags.READABLE)
	def monitor_height(self):
		"""
		Height of the monitor.
		"""
		return self._monitor_height

	@GObject.Property(type=bool, default=False)
	def hexpand(self):
		"""
		Whether to expand the surface horizontally.
		"""
		return self._hexpand

	@hexpand.setter
	def set_hexpand(self, value):
		"""
		Changes whether to expand the surface horizontally.
		"""
		self._hexpand = value

	@GObject.Property(type=bool, default=False)
	def vexpand(self):
		"""
		Whether to expand the surface vertically.
		"""
		return self._vexpand

	@vexpand.setter
	def set_vexpand(self, value):
		"""
		Changes whether to expand the surface vertically.
		"""
		self._vexpand = value
