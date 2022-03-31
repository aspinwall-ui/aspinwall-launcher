# coding: utf-8
"""Contains window creation code for the Aspinwall launcher"""
from gi import require_version as gi_require_version
gi_require_version("Gtk", "4.0")
gi_require_version('Adw', '1')
from gi.repository import Adw, Gtk, Gio
from pathlib import Path
import os

from aspinwall.launcher.config import config
from aspinwall.widgets.loader import load_widgets

# The ClockBox, WidgetBox and AppChooser classes are imported to avoid
# "invalid object type" errors.
from aspinwall.launcher.launcher_boxes import ClockBox, WidgetBox # noqa: F401
from aspinwall.launcher.app_chooser import AppChooser # noqa: F401
from aspinwall.launcher.wallpaper import Wallpaper # noqa: F401
from aspinwall.launcher.settings import LauncherSettings
from aspinwall.launcher.about import AboutAspinwall

win = None
running = False
_version = 0

@Gtk.Template(resource_path='/org/dithernet/aspinwall/launcher/ui/launcher.ui')
class Launcher(Gtk.ApplicationWindow):
	"""Base class for launcher window."""
	__gtype_name__ = 'Launcher'

	launcher_wallpaper_overlay = Gtk.Template.Child()
	wallpaper = Gtk.Template.Child('launcher_wallpaper')

	launcher_flap = Gtk.Template.Child()

	clockbox = Gtk.Template.Child()
	widgetbox = Gtk.Template.Child()
	app_chooser = Gtk.Template.Child()
	app_chooser_show = Gtk.Template.Child()

	def __init__(self, app, in_shell=False):
		"""Initializes the launcher window."""
		super().__init__(
			application=app,
			title='aspinwall-shell'
		)

		self.app_chooser_show.connect('clicked', self.show_app_chooser)

		self.open_settings_action = Gio.SimpleAction.new("open_settings", None)
		self.open_settings_action.connect('activate', self.open_settings)

		self.about_aspinwall_action = Gio.SimpleAction.new("about_aspinwall", None)
		self.about_aspinwall_action.connect('activate', self.open_about)

		self.add_action(self.widgetbox._show_chooser_action)
		self.add_action(self.widgetbox._management_mode_action)
		self.add_action(self.open_settings_action)
		self.add_action(self.about_aspinwall_action)

		self.launcher_wallpaper_overlay.set_measure_overlay(self.launcher_flap, True)

	def show_app_chooser(self, *args):
		"""Shows the app chooser."""
		# Reload apps, clear search
		self.app_chooser.search.set_text('')
		self.app_chooser.update_model()
		# Show chooser
		self.launcher_flap.set_reveal_flap(True)
		self.app_chooser.search.grab_focus()

	def open_settings(self, *args):
		"""Opens the launcher settings window."""
		settings_window = LauncherSettings()
		settings_window.set_transient_for(self)
		settings_window.present()

	def open_about(self, *args):
		"""Opens the about window."""
		about_dialog = AboutAspinwall()
		about_dialog.set_version(_version)
		about_dialog.show()

def on_theme_preference_change(*args):
	"""Called when the theme preference changes."""
	theme_preference = config['theme-preference']
	style_manager = Adw.StyleManager.get_default()
	if theme_preference == 1:
		style_manager.set_color_scheme(Adw.ColorScheme.FORCE_LIGHT)
	elif theme_preference == 2:
		style_manager.set_color_scheme(Adw.ColorScheme.FORCE_DARK)
	else:
		style_manager.set_color_scheme(Adw.ColorScheme.DEFAULT)

def launcher_setup():
	"""Commands that are launched before the launcher window is created."""
	# Set up default wallpapers
	if config['available-wallpapers'][0] == 'fixme':
		wallpaper_files = []
		wallpaper_paths = []
		for filetype in ['jpg', 'png']:
			wallpaper_paths += list(Path('/usr/share/backgrounds').rglob('*.' + filetype))

		for wallpaper in wallpaper_paths:
			wallpaper_files.append(str(wallpaper))
		config['available-wallpapers'] = wallpaper_files

	if config['wallpaper-path'] == 'fixme':
		wallpaper_files = config['available-wallpapers']
		if wallpaper_files:
			config['wallpaper-path'] = wallpaper_files[0]
		else:
			config['wallpaper-path'] = ''
			config['wallpaper-style'] = 0 # solid color

	load_widgets()

def on_activate(app):
	global running
	if running:
		return False
	running = True

	launcher_setup()

	global win
	win = Launcher(app)

	win.present()

	if 'GTK_DEBUG' not in os.environ or not os.environ['GTK_DEBUG']:
		win_surface = win.get_surface()
		win.set_size_request(win_surface.get_width(), win_surface.get_height())
		win.fullscreen()
	else:
		win.set_size_request(1270, 720)

def main(version):
	global _version
	_version = version
	app = Adw.Application(application_id='org.dithernet.aspinwall.Launcher')
	app.set_resource_base_path('/org/dithernet/aspinwall/stylesheet')
	style_manager = app.get_style_manager()
	on_theme_preference_change()
	config.connect('changed::theme-preference', on_theme_preference_change)
	style_manager.connect('notify::color-scheme', on_theme_preference_change)
	app.connect('activate', on_activate)
	app.run()
