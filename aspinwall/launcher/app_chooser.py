# coding: utf-8
"""
Contains code for the app chooser.
"""
from gi.repository import Gdk, Gio, Gtk
import os

@Gtk.Template(filename=os.path.join(os.path.dirname(__file__), 'ui', 'appicon.ui'))
class AppIcon(Gtk.Box):
	"""Contains an app icon for the app chooser."""
	__gtype_name__ = 'AppIcon'

	app = None
	app_icon = Gtk.Template.Child()
	app_name = Gtk.Template.Child()

	def init(self, app=None):
		"""Initializes an AppIcon."""
		super().__init__()

	def bind_to_app(self, app):
		"""Fills the AppIcon with an app's information."""
		self.app = app
		self.app_icon.set_from_icon_name(app.get_string('Icon'))
		self.app_name.set_label(app.get_string('Name'))


@Gtk.Template(filename=os.path.join(os.path.dirname(__file__), 'ui', 'appchooser.ui'))
class AppChooser(Gtk.Revealer):
	"""App chooser widget."""
	__gtype_name__ = 'AppChooser'

	app_grid_container = Gtk.Template.Child()

	def __init__(self):
		"""Initializes an app chooser."""
		super().__init__()

		store = Gio.ListStore(item_type=Gio.AppInfo)
		appinfo = Gio.AppInfo.get_all()
		for app in appinfo:
			if not Gio.AppInfo.should_show(app):
				continue
			store.append(app)

		factory = Gtk.SignalListItemFactory()
		factory.connect('setup', self.setup)
		factory.connect('bind', self.bind)

		app_grid = Gtk.GridView(model=Gtk.SingleSelection(model=store), factory=factory)

		app_grid.set_min_columns(3)
		app_grid.set_max_columns(3)
		app_grid.set_single_click_activate(True)
		app_grid.set_enable_rubberband(False)

		app_grid.connect('activate', self.activate)

		self.app_grid_container.set_child(app_grid)

	def setup(self, factory, list_item):
		"""Sets up the app grid."""
		list_item.set_child(AppIcon())

	def bind(self, factory, list_item):
		"""Binds the list items in the app grid."""
		app_icon = list_item.get_child()
		application = list_item.get_item()
		app_icon.bind_to_app(application)

	def activate(self, app_grid, app_position):
		"""Opens the app selected in the app grid."""
		app_info = app_grid.get_model().get_item(app_position)
		context = Gdk.Display.get_app_launch_context(app_grid.get_display())
		app_info.launch(None, context)

	@Gtk.Template.Callback()
	def hide(self, *args):
		"""Hides the app chooser."""
		self.set_reveal_child(False)
