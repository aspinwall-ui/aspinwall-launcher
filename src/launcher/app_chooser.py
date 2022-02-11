# coding: utf-8
"""
Contains code for the app chooser.
"""
from gi.repository import Gdk, GLib, Gio, Gtk
import os

from aspinwall.launcher.config import config

# Used by AppIcon to find the app chooser revealer
app_chooser = None

@Gtk.Template(resource_path='/org/dithernet/aspinwall/launcher/ui/appicon.ui')
class AppIcon(Gtk.FlowBoxChild):
	"""Contains an app icon for the app chooser."""
	__gtype_name__ = 'AppIcon'

	app = None
	app_icon = Gtk.Template.Child()
	app_name = Gtk.Template.Child()

	popover = Gtk.Template.Child()

	def __init__(self, app=None):
		"""Initializes an AppIcon."""
		super().__init__()
		if app.get_filename() in config['favorite-apps']:
			self.is_favorite = True
		else:
			self.is_favorite = False

		if app:
			self.bind_to_app(app)

	def bind_to_app(self, app):
		"""Fills the AppIcon with an app's information."""
		self.app = app
		self.app_icon.set_from_gicon(app.get_icon())
		self.app_name.set_label(app.get_name())

		longpress_gesture = Gtk.GestureLongPress()
		longpress_gesture.set_propagation_phase(Gtk.PropagationPhase.CAPTURE)
		longpress_gesture.connect('pressed', self.show_menu)

		self.add_controller(longpress_gesture)

		# Set up context menu actions
		self.install_action('favorite', None, self.favorite)
		self.install_action('unfavorite', None, self.unfavorite)

		if self.is_favorite:
			self.action_set_enabled('favorite', False)
		else:
			self.action_set_enabled('unfavorite', False)

	def favorite(self, app_icon, *args):
		"""Adds the app to favorites."""
		config['favorite-apps'] = config['favorite-apps'] + [app_icon.app.get_filename()]
		app_chooser.update_model()

	def unfavorite(self, app_icon, *args):
		"""Removes the app from favorites."""
		new_list = config['favorite-apps'].copy()
		new_list.remove(app_icon.app.get_filename())

		config['favorite-apps'] = new_list

		app_chooser.update_model()

	@Gtk.Template.Callback()
	def run(self, *args):
		"""Opens the app represented by the app icon."""
		context = Gdk.Display.get_app_launch_context(self.get_display())
		self.app.launch(None, context)
		app_chooser.hide()

	def show_menu(self, event_controller, *args):
		"""Shows the app icon menu."""
		self.popover.show()

@Gtk.Template(resource_path='/org/dithernet/aspinwall/launcher/ui/appchooser.ui')
class AppChooser(Gtk.Box):
	"""App chooser widget."""
	__gtype_name__ = 'AppChooser'

	app_grid = Gtk.Template.Child()
	favorites_revealer = Gtk.Template.Child()
	favorites_grid = Gtk.Template.Child()
	search = Gtk.Template.Child()

	def __init__(self):
		"""Initializes an app chooser."""
		super().__init__()

		# Set up store for app model and favorite model; the stores are
		# filled in the update_model function
		self.store = Gio.ListStore(item_type=Gio.AppInfo)
		self.favorites_model = Gio.ListStore(item_type=Gio.AppInfo)

		# Set up sort model
		self.sort_model = Gtk.SortListModel(model=self.store)
		self.sorter = Gtk.CustomSorter.new(self.sort_func, None)
		self.sort_model.set_sorter(self.sorter)

		# Set up filter model
		filter_model = Gtk.FilterListModel(model=self.sort_model)
		self.filter = Gtk.CustomFilter.new(self.filter_by_name, filter_model)
		filter_model.set_filter(self.filter)
		self.search.connect('search-changed', self.search_changed)

		self.model = filter_model

		# Set up app grid
		self.app_grid.bind_model(self.model, self.bind, None)

		# Set up favorites grid
		self.favorites_grid.bind_model(self.favorites_model, self.bind, None)

		global app_chooser
		app_chooser = self

	def update_model(self):
		"""Updates the favorites and app grid models."""
		self.store.remove_all()
		appinfo = Gio.AppInfo.get_all()

		self.favorites_model.remove_all()
		favorites = config['favorite-apps']
		found_favorites = []

		for app in appinfo:
			if app.get_filename() in favorites:
				found_favorites.append(app.get_filename())
				self.favorites_model.append(app)
			if not Gio.AppInfo.should_show(app):
				continue
			self.store.append(app)

		# Clear out old favorites
		not_found_favorites = list(set(favorites) - set(found_favorites))
		if not_found_favorites:
			new_favorites = favorites.copy()
			for filename in not_found_favorites:
				new_favorites.remove(filename)
			config['favorite-apps'] = new_favorites

		self.sort_model.set_model(self.store)

	def bind(self, app, *args):
		"""Binds the list items in the app grid."""
		app_icon = AppIcon(app)
		return app_icon

	def filter_by_name(self, appinfo, user_data):
		"""Fill-in for custom filter for app grid."""
		query = self.search.get_text()
		if not query:
			if appinfo.get_filename() in config['favorite-apps']:
				return False
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

	def search_changed(self, search_entry, *args):
		"""Notifies the filter about search changes."""
		if search_entry.get_text():
			self.favorites_revealer.set_reveal_child(False)
		else:
			self.favorites_revealer.set_reveal_child(True)

		self.filter.changed(Gtk.FilterChange.DIFFERENT)
		# Select first item in list
		first_item = self.app_grid.get_first_child()
		if first_item:
			first_item.grab_focus()
		# TODO: Scroll back to top of list

	@Gtk.Template.Callback()
	def hide(self, *args):
		"""Hides the app chooser."""
		self.get_parent().set_reveal_flap(False)
