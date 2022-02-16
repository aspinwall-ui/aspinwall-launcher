# coding: utf-8
"""
Contains code for the launcher settings window. Not to be confused with the
settings access backend, which is set up in config.py.
"""
from gi.repository import Gtk, Adw

from aspinwall.launcher.config import config

@Gtk.Template(resource_path='/org/dithernet/aspinwall/launcher/ui/settings.ui')
class LauncherSettings(Adw.PreferencesWindow):
	"""Launcher settings window."""
	__gtype_name__ = 'LauncherSettings'

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

		self.time_format_entry.set_text(config['time-format'])
		self.date_format_entry.set_text(config['date-format'])

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
