# coding: utf-8
"""
Contains code for the window switcher.
"""
from gi.repository import GdkPixbuf, Gtk, GObject

from aspinwall.launcher.wallpaper import Wallpaper
from aspinwall.shell.interfaces.manager import get_interface_manager
from aspinwall.shell.surface import Surface

@Gtk.Template(resource_path='/org/dithernet/aspinwall/shell/ui/windowview.ui')
class WindowView(Gtk.Box):
	"""
	Shows an open window's content and action buttons (close, etc.)
	"""
	__gtype_name__ = 'WindowView'

	window = None
	window_title = Gtk.Template.Child()
	window_icon = Gtk.Template.Child()
	window_preview = Gtk.Template.Child()

	def __init__(self):
		"""Initializes the WindowView."""
		super().__init__()

	def bind_to_window(self, window):
		"""Binds the WindowView to a window."""
		self.window = window
		window.bind_property('title', self.window_title, 'label',
			GObject.BindingFlags.SYNC_CREATE
		)
		if window.props.icon_pixbuf:
			scaled_icon = window.props.icon_pixbuf.scale_simple(
				24, 24, GdkPixbuf.InterpType.BILINEAR
			)

			self.window_icon.set_from_pixbuf(scaled_icon)
			self.window_preview.set_from_pixbuf(scaled_icon)

	def focus_window(self, *args):
		"""Focuses the window represented by the icon."""
		self.window.focus()

	@Gtk.Template.Callback()
	def close_window(self, *args):
		"""Closes the window represented by the icon."""
		self.window.close()

window_switcher = None

@Gtk.Template(resource_path='/org/dithernet/aspinwall/shell/ui/windowswitcher.ui')
class WindowSwitcher(Surface):
	"""
	Shows open windows and allows switching between them.
	"""
	__gtype_name__ = 'WindowSwitcher'

	wallpaper_bin = Gtk.Template.Child()
	wallpaper = None

	_opened = False

	container_revealer = Gtk.Template.Child()
	window_list = Gtk.Template.Child()

	def __init__(self, app):
		"""Initializes the window switcher."""
		super().__init__(
			application=app,
			valign=Gtk.Align.START,
			hexpand=True,
			vexpand=True,
			visible=False,
			top=36
		)

		global window_switcher
		window_switcher = self

		interface_manager = get_interface_manager()
		window_interface = interface_manager.get_interface_by_name('WindowInterface')
		self.window_store = window_interface.windows

		# Set up filter
		self.filtered_store = Gtk.FilterListModel(model=self.window_store)
		self.filter = Gtk.CustomFilter.new(self.filter_window, self.window_store)
		self.filtered_store.set_filter(self.filter)
		self.window_store.connect('items-changed', self.update_filter)

		# Set up factory/window list
		factory = Gtk.SignalListItemFactory()
		factory.connect('setup', self.window_setup)
		factory.connect('bind', self.window_bind)

		self.window_list.set_model(Gtk.SingleSelection(model=self.filtered_store))
		self.window_list.set_factory(factory)
		self.window_list.connect('activate', self.focus_window)

		self.connect('map', self.load_wallpaper)
		self.connect('unmap', self.unload_wallpaper)

	def show_switcher(self, *args):
		"""Shows the window switcher."""
		self._opened = True
		self.notify('opened')
		self.show_and_focus()
		self.set_visible(True)
		self.container_revealer.set_reveal_child(True)

	def close_switcher(self, *args):
		"""Closes the window switcher."""
		self._opened = False
		self.notify('opened')
		self.container_revealer.set_reveal_child(False)
		self.set_visible(False)
		self.close()

	def window_setup(self, factory, list_item):
		"""Sets up a window list item."""
		list_item.set_child(WindowView())

	def window_bind(self, factory, list_item):
		"""Binds the window list item to a window."""
		window_view = list_item.get_child()
		window = list_item.get_item()
		window_view.bind_to_window(window)

	def focus_window(self, list, window_no):
		list.get_model().get_item(window_no).focus()

	def update_filter(self, *args):
		"""Convenience function that forces a filter update."""
		self.filter.changed(Gtk.FilterChange.DIFFERENT)

	def filter_window(self, window, *args):
		"""
		Returns True if the window should be shown in the window switcher,
		False otherwise.
		"""
		return window.props.visible

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

	@GObject.Property(type=bool, default=False)
	def opened(self):
		"""Whether the window switcher is currently open or not."""
		return self._opened

	@opened.setter
	def set_opened(self, value):
		"""Sets whether the window switcher is currently open or not."""
		if value is True:
			self.show_switcher()
		else:
			self.close_switcher()
