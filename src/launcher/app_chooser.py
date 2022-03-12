# coding: utf-8
"""
Contains code for the app chooser.
"""
from gi.repository import Gdk, GLib, Gio, Gtk

from aspinwall.launcher.config import config

# Used by AppIcon to find the app chooser revealer
app_chooser = None

def app_info_to_filenames(appinfo):
	"""Takes a list of apps and returns their filenames."""
	output = {}
	for app in appinfo:
		output[app.get_filename()] = app
	return output

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
		self.popover.present()
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
		if app_icon.app.get_filename() not in config['favorite-apps']:
			config['favorite-apps'] = config['favorite-apps'] + [app_icon.app.get_filename()]
			self.is_favorite = True

			self.action_set_enabled('unfavorite', True)
			self.action_set_enabled('favorite', False)

			app_chooser.filter.changed(Gtk.FilterChange.MORE_STRICT)
			app_chooser.favorites_filter.changed(Gtk.FilterChange.LESS_STRICT)

			if not app_chooser.in_search:
				app_chooser.favorites_revealer.set_reveal_child(True)

	def unfavorite(self, app_icon, *args):
		"""Removes the app from favorites."""
		if app_icon.app.get_filename() in config['favorite-apps']:
			new_list = config['favorite-apps'].copy()
			new_list.remove(app_icon.app.get_filename())
			config['favorite-apps'] = new_list
			self.is_favorite = False

			self.action_set_enabled('favorite', True)
			self.action_set_enabled('unfavorite', False)

			app_chooser.filter.changed(Gtk.FilterChange.LESS_STRICT)
			app_chooser.favorites_filter.changed(Gtk.FilterChange.MORE_STRICT)

			if not new_list:
				app_chooser.favorites_revealer.set_reveal_child(False)

	@Gtk.Template.Callback()
	def run(self, *args):
		"""Opens the app represented by the app icon."""
		context = Gdk.Display.get_app_launch_context(self.get_display())
		self.app.launch(None, context)
		app_chooser.hide()

	def show_menu(self, event_controller, *args):
		"""Shows the app icon menu."""
		# FIXME: Newly added icons seem to keep the unfavorite action enabled;
		# this fixes it, but there is probably a deeper root cause
		if self.is_favorite:
			self.action_set_enabled('favorite', False)
		else:
			self.action_set_enabled('unfavorite', False)
		self.popover.show()

@Gtk.Template(resource_path='/org/dithernet/aspinwall/launcher/ui/appchooser.ui')
class AppChooser(Gtk.Box):
	"""App chooser widget."""
	__gtype_name__ = 'AppChooser'

	# Whether we are currently searching or not
	in_search = False

	app_grid = Gtk.Template.Child()
	favorites_revealer = Gtk.Template.Child()
	favorites_grid = Gtk.Template.Child()
	search = Gtk.Template.Child()

	def __init__(self):
		"""Initializes an app chooser."""
		super().__init__()

		# Set up store for app model
		self.store = Gio.ListStore(item_type=Gio.AppInfo)
		self.fill_model()

		# Set up sort model
		self.sort_model = Gtk.SortListModel(model=self.store)
		self.sorter = Gtk.CustomSorter.new(self.sort_func, None)
		self.sort_model.set_sorter(self.sorter)

		# Set up filter model
		filter_model = Gtk.FilterListModel(model=self.sort_model)
		self.filter = Gtk.CustomFilter.new(self.filter_by_name, filter_model)
		filter_model.set_filter(self.filter)
		self.search.connect('search-changed', self.search_changed)

		# Set up favorites model
		self.favorites_model = Gtk.FilterListModel(model=self.store)
		self.favorites_filter = Gtk.CustomFilter.new(
			self.is_favorite,
			self.favorites_model
		)
		self.favorites_model.set_filter(self.favorites_filter)

		self.model = filter_model

		# Set up app grid
		self.app_grid.bind_model(self.model, self.bind, None)

		# Set up favorites grid
		self.favorites_grid.bind_model(self.favorites_model, self.bind, None)

		# Show/hide the favorites depending on whether there are any
		if config['favorite-apps']:
			self.favorites_revealer.set_reveal_child(True)
		else:
			self.favorites_revealer.set_reveal_child(False)

		global app_chooser
		app_chooser = self

	def fill_model(self):
		"""Fills the favorites and app grid models."""
		appinfo = Gio.AppInfo.get_all()
		self.store.remove_all()

		for app in appinfo:
			if not Gio.AppInfo.should_show(app):
				continue
			self.store.append(app)

		self.previous_appinfo = self.store

	def update_model(self):
		"""Updates the app grid model."""
		_appinfo = Gio.ListStore(item_type=Gio.AppInfo)
		for app in Gio.AppInfo.get_all():
			if app.should_show():
				_appinfo.append(app)

		appinfo = app_info_to_filenames(_appinfo)
		previous_appinfo = app_info_to_filenames(self.previous_appinfo)

		# Comparing the stores to each other erroneously returns True
		if previous_appinfo.keys() != appinfo.keys():
			new_appinfo = list(set(previous_appinfo.keys()) - set(appinfo.keys())) + \
				list(set(appinfo.keys()) - set(previous_appinfo.keys()))
			for app_name in new_appinfo:
				if app_name in previous_appinfo:
					# App removed
					find = self.store.find(previous_appinfo[app_name])
					if find[0]:
						self.store.remove(find[1])
					if app_name in config['favorite-apps']:
						new_list = config['favorite-apps'].copy()
						new_list.remove(app_name)
						config['favorite-apps'] = new_list
					self.sorter.changed(Gtk.SorterChange.DIFFERENT)
					self.filter.changed(Gtk.FilterChange.DIFFERENT)
					self.favorites_filter.changed(Gtk.FilterChange.DIFFERENT)
				else:
					# App added
					self.store.append(appinfo[app_name])
					self.sorter.changed(Gtk.SorterChange.DIFFERENT)
					self.filter.changed(Gtk.FilterChange.DIFFERENT)
					self.favorites_filter.changed(Gtk.FilterChange.DIFFERENT)

		if config['favorite-apps'] and not self.in_search:
			self.favorites_revealer.set_reveal_child(True)
		else:
			self.favorites_revealer.set_reveal_child(False)

	def bind(self, app, *args):
		"""Binds the list items in the app grid."""
		return AppIcon(app)

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

	def is_favorite(self, appinfo, *args):
		"""
		Takes a Gio.AppInfo and returns whether the app is in favorites or not.
		"""
		if appinfo.get_filename() in config['favorite-apps']:
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
			self.in_search = True
			self.favorites_revealer.set_reveal_child(False)
		else:
			self.in_search = False
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
