# coding: utf-8
"""
Common classes for interfaces that handle windows.
"""
from gi.repository import Gio, GObject

from aspinwall.shell.interfaces import Interface

class Window(GObject.Object):
	"""
	Contains information about a window.
	"""
	__gtype_name__ = 'Window'

	# Placeholders for basic data; this is provided by objects that
	# inherit from this one
	_title = ''
	_visible = True

	def __init__(self, title='', icon_pixbuf=None, visible=True):
		"""Initializes a Window object."""
		super().__init__()
		self._title = title
		self.notify('title')

		self._icon_pixbuf = icon_pixbuf
		self.notify('icon-pixbuf')

		self._visible = visible
		self.notify('visible')

	@GObject.Property(type=str, flags=GObject.ParamFlags.READABLE)
	def title(self):
		"""The window's title."""
		return self._title

	@GObject.Property(flags=GObject.ParamFlags.READABLE)
	def icon_pixbuf(self):
		"""The window's icon, as a GdkPixbuf."""
		return self._icon_pixbuf

	@GObject.Property(type=bool, flags=GObject.ParamFlags.READABLE, default=True)
	def visible(self):
		"""Whether the window should be visible in the window switcher."""
		return self._visible

	def close(self):
		"""Closes the window represented by this object."""
		raise NotImplementedError

	def focus(self):
		"""Focuses the window represented by this object."""
		raise NotImplementedError

class ProtocolSpecificInterface(GObject.Object):
	"""
	Base class for protocol-specific interfaces.
	"""
	__gtype_name__ = 'ProtocolSpecificInterface'

	def __init__(self, window_interface):
		"""
		Initializes a protocol-specific interface.

		The window_interface kwarg must be set to the WindowInterface
		that the protocol-specific interface is owned by.
		"""
		super().__init__()
		self.window_interface = window_interface
		self.windows = window_interface.windows

class WindowInterface(Interface):
	"""
	Main window list interface.

	Actually managing the window list is up to the window manager protocol-
	specific interfaces. This interface provides an unified way to communicate
	with them.
	"""
	__gtype_name__ = 'WindowInterface'

	def __init__(self):
		"""Initializes the WindowInterface."""
		super().__init__()
		self.windows = Gio.ListStore(item_type=Window)

		# Set up the actual window manager protocol-specific interface.
		# Currently, only X11 is supported; in the future, when we
		# add Wayland support, this part of the init function will need
		# to be expanded to include Wayland detection.

		from aspinwall.shell.interfaces.x11window import X11WindowInterface
		self.specific_interface = X11WindowInterface(self)

	def update_windows(self):
		"""Updates the window list."""
		self.specific_interface.update_windows()
