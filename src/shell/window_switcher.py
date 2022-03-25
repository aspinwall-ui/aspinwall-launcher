# coding: utf-8
"""
Contains code for the window switcher.
"""
from gi.repository import Gtk

from aspinwall.launcher.wallpaper import Wallpaper # noqa: F401
from aspinwall.shell.surface import Surface

@Gtk.Template(resource_path='/org/dithernet/aspinwall/shell/ui/windowview.ui')
class WindowView(Gtk.Box):
	"""
	Shows an open window's content and action buttons (close, etc.)
	"""
	__gtype_name__ = 'WindowView'

	def __init__(self):
		"""Initializes the WindowView."""
		super().__init__()

	def bind_to_window(self, window):
		"""Binds the WindowView to a window."""
		pass

@Gtk.Template(resource_path='/org/dithernet/aspinwall/shell/ui/windowswitcher.ui')
class WindowSwitcher(Surface):
	"""
	Shows open windows and allows switching between them.
	"""
	__gtype_name__ = 'WindowSwitcher'

	wallpaper_bin = Gtk.Template.Child()
	wallpaper = None

	def __init__(self, app):
		"""Initializes the window switcher."""
		super().__init__(
			application=app,
			valign=Gtk.Align.START,
			hexpand=True,
			vexpand=True,
			visible=False
		)

		self.connect('map', self.load_wallpaper)
		self.connect('unmap', self.unload_wallpaper)

	def load_wallpaper(self, *args):
		"""Loads the wallpaper when the window switcher is opened."""
		self.wallpaper = Wallpaper()
		self.wallpaper_bin.set_child(self.wallpaper)

	def unload_wallpaper(self, *args):
		"""Unloads the wallpaper when the window switcher is closed."""
		self.wallpaper_bin.set_child(None)
		if self.wallpaper:
			self.wallpaper._destroy()
			self.wallpaper.unrealize()
			self.wallpaper = None
