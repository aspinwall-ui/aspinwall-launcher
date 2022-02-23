# coding: utf-8
"""
Contains code for the launcher settings window. Not to be confused with the
settings access backend, which is set up in config.py.
"""
from gi.repository import Adw, GdkPixbuf, Gtk, Gio
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
		bind_thread = threading.Thread(target=self.bind, args=[wallpaper_path])
		bind_thread.start()

	def bind(self, wallpaper_path):
		"""Binds the wallpaper icon to a wallpaper from the path."""
		self.wallpaper = wallpaper_path

		pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_size(
			wallpaper_path,
			144, 144
		)

		self.picture.set_pixbuf(pixbuf)

@Gtk.Template(resource_path='/org/dithernet/aspinwall/launcher/ui/settings.ui')
class LauncherSettings(Adw.PreferencesWindow):
	"""Launcher settings window."""
	__gtype_name__ = 'LauncherSettings'

	wallpaper_grid = Gtk.Template.Child()
	system_wallpaper_settings_toggle = Gtk.Template.Child()
	theme_toggle_start = Gtk.Template.Child()
	theme_toggle_end = Gtk.Template.Child()
	follow_system_theme_toggle = Gtk.Template.Child()

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

		wallpaper_store = Gtk.StringList()
		wallpaper_store.splice(0, 0, config['available-wallpapers'])

		self.wallpaper_grid.bind_model(
			wallpaper_store,
			self.wallpaper_bind,
			None,
			self.wallpaper_free
		)

		if bg_config:
			self.system_wallpaper_settings_toggle.set_active(config['use-gnome-background'])
		else:
			self.system_wallpaper_settings_toggle.set_active(False)
			self.system_wallpaper_settings_toggle.set_sensitive(False)

		self.time_format_entry.set_text(config['time-format'])
		self.date_format_entry.set_text(config['date-format'])

	def wallpaper_bind(self, wallpaper_path_string, *args):
		"""Returns a WallpaperIcon for the path in the given StringObject."""
		wallpaper_path = wallpaper_path_string.get_string()
		return WallpaperIcon(wallpaper_path)

	def wallpaper_free(self, *args):
		print('Free:', args)

	@Gtk.Template.Callback()
	def set_wallpaper_from_grid(self, flowbox, wallpaper_icon):
		config['wallpaper-path'] = wallpaper_icon.wallpaper

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
	def change_time_format(self, text_field, *args):
		"""Changes the clockbox time format based on the text field content."""
		config['time-format'] = text_field.get_text()

	@Gtk.Template.Callback()
	def change_date_format(self, text_field, *args):
		"""Changes the clockbox date format based on the text field content."""
		config['date-format'] = text_field.get_text()
