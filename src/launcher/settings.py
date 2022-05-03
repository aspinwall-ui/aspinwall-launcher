# coding: utf-8
"""
Contains code for the launcher settings window. Not to be confused with the
settings access backend, which is set up in config.py.
"""
from gi.repository import Adw, GdkPixbuf, Gtk, Gdk, GObject
import threading

from aspinwall.launcher.config import config, bg_config

@Gtk.Template(resource_path='/org/dithernet/aspinwall/launcher/ui/wallpapericon.ui')
class WallpaperIcon(Gtk.FlowBoxChild):
	"""Wallpaper icon for the wallpaper grid."""
	__gtype_name__ = 'WallpaperIcon'

	picture = Gtk.Template.Child()

	def __init__(self, wallpaper_path):
		"""Initializes the wallpaper icon."""
		super().__init__()

		self.drag_source = Gtk.DragSource(actions=Gdk.DragAction.MOVE)
		self.drag_source.connect("prepare", self.drag_prepare)
		self.drag_source.connect("drag-begin", self.drag_begin)
		self.add_controller(self.drag_source)

		self.drop_target = Gtk.DropTarget(actions=Gdk.DragAction.MOVE)
		self.drop_target.set_gtypes([GObject.TYPE_STRING])
		self.drop_target.connect("drop", self.drop)
		self.add_controller(self.drop_target)

		bind_thread = threading.Thread(target=self.bind, args=[wallpaper_path])
		bind_thread.start()

		self.connect('unmap', self._destroy)

	def _destroy(self, *args):
		"""Removes the stored pixbuf."""
		self.picture = None
		self.pixbuf = None

	def bind(self, wallpaper_path):
		"""Binds the wallpaper icon to a wallpaper from the path."""
		self.wallpaper = wallpaper_path

		self.pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_size(
			wallpaper_path,
			144, 144
		)

		self.picture.set_pixbuf(self.pixbuf)

	@Gtk.Template.Callback()
	def remove_from_available(self, *args):
		"""Removes the wallpaper from available wallpapers."""
		new_config = config['available-wallpapers'].copy()
		new_config.remove(self.wallpaper)
		config['available-wallpapers'] = new_config

	# Drag source
	def drag_prepare(self, *args):
		return Gdk.ContentProvider.new_for_value(self.wallpaper)

	def drag_begin(self, drag_source, *args):
		drag_source.set_icon(
			Gtk.WidgetPaintable.new(self),
			self.get_width() / 2, self.get_height() / 2
		)

	# Drop target
	def drop(self, target, value, *args):
		wallpaper_path = value
		new_config = config['available-wallpapers'].copy()
		new_config.insert(
			new_config.index(self.wallpaper),
			new_config.pop(new_config.index(wallpaper_path))
		)
		config['available-wallpapers'] = new_config

@Gtk.Template(resource_path='/org/dithernet/aspinwall/launcher/ui/settings.ui')
class LauncherSettings(Adw.PreferencesWindow):
	"""Launcher settings window."""
	__gtype_name__ = 'LauncherSettings'

	wallpaper_grid = Gtk.Template.Child()
	wallpaper_style_combobox = Gtk.Template.Child()
	wallpaper_color_button = Gtk.Template.Child()
	slideshow_mode_toggle = Gtk.Template.Child()
	slideshow_switch_delay_combobox = Gtk.Template.Child()
	system_wallpaper_settings_toggle = Gtk.Template.Child()

	theme_toggle_start = Gtk.Template.Child()
	theme_toggle_end = Gtk.Template.Child()
	follow_system_theme_toggle = Gtk.Template.Child()

	idle_mode_delay_combobox = Gtk.Template.Child()

	clock_size_combobox = Gtk.Template.Child()
	time_format_entry = Gtk.Template.Child()
	date_format_entry = Gtk.Template.Child()

	def __init__(self):
		"""Initializes the settings window."""
		super().__init__()

		# Set up settings
		if config['theme-preference'] == 2:
			self.theme_toggle_start.set_active(False)
			self.theme_toggle_end.set_active(True)
		elif config['theme-preference'] == 1:
			self.theme_toggle_start.set_active(True)
			self.theme_toggle_end.set_active(False)
		else:
			self.theme_toggle_start.set_active(True)
			self.follow_system_theme_toggle.set_active(True)

		self.wallpaper_store = Gtk.StringList()
		self.wallpaper_store.splice(0, 0, config['available-wallpapers'])
		self.wallpaper_sort_model = Gtk.SortListModel(model=self.wallpaper_store)
		self.wallpaper_sorter = Gtk.CustomSorter.new(self.wallpaper_sort_func, None)
		self.wallpaper_sort_model.set_sorter(self.wallpaper_sorter)
		self.wallpaper_grid.bind_model(
			self.wallpaper_sort_model,
			self.wallpaper_bind,
			None
		)
		config.connect('changed::available-wallpapers', self.update_wallpaper_grid)

		self.refresh_wallpaper_grid_selection()
		config.connect('changed::wallpaper-path', self.refresh_wallpaper_grid_selection)

		self.wallpaper_style_combobox.set_active_id(str(config['wallpaper-style']))

		self.wallpaper_color_button.set_use_alpha(False)
		bg_color = Gdk.RGBA()
		bg_color.parse('rgb' + str(config['wallpaper-color']))
		self.wallpaper_color_button.set_rgba(bg_color)

		if bg_config:
			self.system_wallpaper_settings_toggle.set_active(config['use-gnome-background'])
		else:
			self.system_wallpaper_settings_toggle.set_active(False)
			self.system_wallpaper_settings_toggle.set_sensitive(False)

		self.slideshow_mode_toggle.set_active(config['slideshow-mode'])
		self.clock_size_combobox.set_active(config['clock-size'])
		self.slideshow_switch_delay_combobox.set_active_id(str(config['slideshow-switch-delay']))
		self.idle_mode_delay_combobox.set_active_id(str(config['idle-mode-delay']))

		self.time_format_entry.set_text(config['time-format'])
		self.date_format_entry.set_text(config['date-format'])

	def wallpaper_bind(self, wallpaper_path_string, *args):
		"""Returns a WallpaperIcon for the path in the given StringObject."""
		wallpaper_path = wallpaper_path_string.get_string()
		return WallpaperIcon(wallpaper_path)

	def wallpaper_sort_func(self, a, b, *args):
		"""Sort function for the wallpaper grid."""
		a_index = config['available-wallpapers'].index(a.get_string())
		b_index = config['available-wallpapers'].index(b.get_string())

		if a_index < b_index:
			return -1
		elif a_index > b_index:
			return 1
		else:
			return 0

	def update_wallpaper_grid(self, *args):
		"""Updates the wallpaper grid after a removal/addition."""
		_current_store = list(self.wallpaper_store)
		current_store = []
		# This contains StringObjects, so convert them to strings first
		for item in _current_store:
			current_store.append(item.get_string())
		current_config = config['available-wallpapers'].copy()

		new_wallpapers = list(set(current_store) - set(current_config)) + \
			list(set(current_config) - set(current_store))

		if new_wallpapers:
			# Wallpaper was added/removed
			for wallpaper in new_wallpapers:
				if wallpaper in current_config:
					# Wallpaper added
					self.wallpaper_store.append(wallpaper)
				else:
					# Wallpaper removed
					self.wallpaper_store.remove(current_store.index(wallpaper))

		self.wallpaper_sorter.changed(Gtk.SorterChange.DIFFERENT)

		self.refresh_wallpaper_grid_selection()

		self.queue_draw()

	def refresh_wallpaper_grid_selection(self, *args):
		"""
		Selects the wallpaper provided in wallpaper-path in the wallpaper grid.
		"""
		try:
			self.wallpaper_grid.select_child(
				self.wallpaper_grid.get_child_at_index(
					config['available-wallpapers'].index(
						config['wallpaper-path']
					)
				)
			)
		except ValueError:
			if config['available-wallpapers']:
				self.wallpaper_grid.select_child(
					self.wallpaper_grid.get_child_at_index(0)
				)
			else:
				config['wallpaper-style'] = 0
				self.wallpaper_style_combobox.set_active_id("0")

	@Gtk.Template.Callback()
	def set_slideshow_switch_delay(self, combobox, *args):
		"""Sets the slideshow switch delay."""
		config['slideshow-switch-delay'] = int(combobox.get_active_id())

	@Gtk.Template.Callback()
	def set_idle_mode_delay(self, combobox, *args):
		"""Sets the idle mode switch delay."""
		config['idle-mode-delay'] = int(combobox.get_active_id())

	@Gtk.Template.Callback()
	def set_wallpaper_style(self, combobox, *args):
		"""Sets the wallpaper style settings."""
		config['wallpaper-style'] = int(combobox.get_active_id())

	@Gtk.Template.Callback()
	def set_wallpaper_color(self, button, *args):
		rgba = button.get_rgba()
		config['wallpaper-color'] = [rgba.red * 255, rgba.green * 255, rgba.blue * 255]

	@Gtk.Template.Callback()
	def show_wallpaper_add_dialog(self, *args):
		"""Shows the wallpaper addition dialog."""
		file_dialog = Gtk.FileChooserDialog(
			title=_('Add wallpaper'), # noqa: F821
			action=Gtk.FileChooserAction.OPEN,
		)

		file_dialog.add_buttons(
			# TRANSLATORS: Used for the file chooser dialog for adding wallpapers
			_('_Cancel'), Gtk.ResponseType.CANCEL, # noqa: F821
			# TRANSLATORS: Used for the file chooser dialog for adding wallpapers
			_('_Select'), Gtk.ResponseType.OK # noqa: F821
		)

		file_dialog.set_transient_for(self)
		file_dialog.show()

		file_dialog.connect('response', self.add_wallpaper)

	def add_wallpaper(self, dialog, response):
		"""Callback for the wallpaper addition dialog."""
		if response == Gtk.ResponseType.OK:
			file = dialog.get_file()
			wallpaper_path = file.get_path()
			new_wallpapers = config['available-wallpapers'].copy()
			new_wallpapers.append(wallpaper_path)
			config['available-wallpapers'] = new_wallpapers

		dialog.destroy()

	@Gtk.Template.Callback()
	def set_wallpaper_from_grid(self, flowbox, wallpaper_icon):
		config['wallpaper-path'] = wallpaper_icon.wallpaper
		self.queue_draw()

	@Gtk.Template.Callback()
	def toggle_slideshow_mode(self, switch, *args):
		"""Toggles slideshow mode based on the switch position."""
		if switch.get_active():
			config['slideshow-mode'] = True
		else:
			config['slideshow-mode'] = False

	@Gtk.Template.Callback()
	def toggle_use_system_wallpaper(self, switch, *args):
		"""
		Toggles the 'use system wallpaper' option based on the switch position.
		"""
		if switch.get_active():
			config['use-gnome-background'] = True
		else:
			config['use-gnome-background'] = False

	@Gtk.Template.Callback()
	def toggle_theme(self, button, *args):
		"""
		Changes the theme to light/dark based on the toggle button position.
		"""
		if button.get_active() is False:
			config['theme-preference'] = 2
		else:
			config['theme-preference'] = 1

	@Gtk.Template.Callback()
	def toggle_follow_system_theme(self, button, *args):
		"""
		Sets the 'follow system theme' option based on the check button position.
		"""
		if button.get_active():
			config['theme-preference'] = 0
		else:
			self.toggle_theme(self.theme_toggle_start)

	@Gtk.Template.Callback()
	def set_clock_size(self, combobox, *args):
		"""Sets the clock size.."""
		config['clock-size'] = int(combobox.get_active_id())

	@Gtk.Template.Callback()
	def reset_time_format(self, *args):
		"""Resets the clock format settings to defaults."""
		config.reset('time-format')
		self.time_format_entry.set_text(config['time-format'])

		config.reset('date-format')
		self.date_format_entry.set_text(config['date-format'])

	@Gtk.Template.Callback()
	def change_time_format(self, text_field, *args):
		"""Changes the clockbox time format based on the text field content."""
		config['time-format'] = text_field.get_text()

	@Gtk.Template.Callback()
	def change_date_format(self, text_field, *args):
		"""Changes the clockbox date format based on the text field content."""
		config['date-format'] = text_field.get_text()
