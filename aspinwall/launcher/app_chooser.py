# coding: utf-8
"""
Contains code for the app chooser.
"""
from gi.repository import Gdk, GLib, Gio, Gtk
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
		self.app_icon.set_from_gicon(app.get_icon())
		self.app_name.set_label(app.get_name())

@Gtk.Template(filename=os.path.join(os.path.dirname(__file__), 'ui', 'appchooser.ui'))
class AppChooser(Gtk.Box):
	"""App chooser widget."""
	__gtype_name__ = 'AppChooser'

	app_grid_container = Gtk.Template.Child()
	search = Gtk.Template.Child()

	def __init__(self):
		"""Initializes an app chooser."""
		super().__init__()

		factory = Gtk.SignalListItemFactory()
		factory.connect('setup', self.setup)
		factory.connect('bind', self.bind)

		# Set up model and factory
		store = Gio.ListStore(item_type=Gio.AppInfo)
		appinfo = Gio.AppInfo.get_all()
		for app in appinfo:
			if not Gio.AppInfo.should_show(app):
				continue
			store.append(app)

		# Set up sort model
		self.sort_model = Gtk.SortListModel(model=store)
		self.sorter = Gtk.CustomSorter.new(self.sort_func, None)
		self.sort_model.set_sorter(self.sorter)

		# Set up filter model
		filter_model = Gtk.FilterListModel(model=self.sort_model)
		self.filter = Gtk.CustomFilter.new(self.filter_by_name, filter_model)
		filter_model.set_filter(self.filter)
		self.search.connect('search-changed', self.search_changed)

		self.model = filter_model

		# Set up app grid
		app_grid = Gtk.GridView(model=Gtk.SingleSelection(model=self.model), factory=factory)
		app_grid.set_min_columns(2)
		app_grid.set_max_columns(2)
		app_grid.set_single_click_activate(True)
		app_grid.set_enable_rubberband(False)
		app_grid.add_css_class('app-grid')
		app_grid.connect('activate', self.activate)

		self.app_grid_container.set_child(app_grid)

	def setup(self, factory, list_item):
		"""Sets up the app grid."""
		list_item.set_child(AppIcon())

	def update_model(self):
		"""Updates the app grid model."""
		store = Gio.ListStore(item_type=Gio.AppInfo)
		appinfo = Gio.AppInfo.get_all()
		for app in appinfo:
			if not Gio.AppInfo.should_show(app):
				continue
			store.append(app)

		self.sort_model.set_model(store)

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
		self.hide()

	def filter_by_name(self, appinfo, user_data):
		"""Fill-in for custom filter for app grid."""
		query = self.search.get_text()
		if not query:
			return True
		query = query.casefold()

		if query in appinfo.get_name().casefold():
			return True

		if appinfo.get_generic_name():
			if query in appinfo.get_generic_name().casefold():
				return True

		for keyword in appinfo.get_keywords():
			if query in keyword.casefold():
				return True

		return False

	def sort_func(self, a, b, *args):
		"""Sort function for the app grid icon sorter."""
		a_name = GLib.utf8_casefold(a.get_name(), -1)
		if not a_name:
			a_name = ''
		b_name = GLib.utf8_casefold(b.get_name(), -1)
		if not b_name:
			b_name = ''
		return GLib.utf8_collate(a_name, b_name)

	def search_changed(self, *args):
		"""Notifies the filter about search changes."""
		self.filter.changed(Gtk.FilterChange.DIFFERENT)
		# Select first item in list
		selection_model = self.app_grid_container.get_child().get_model()
		selection_model.set_selected(0)
		# TODO: Scroll back to top of list

	@Gtk.Template.Callback()
	def hide(self, *args):
		"""Hides the app chooser."""
		self.get_parent().set_reveal_flap(False)
