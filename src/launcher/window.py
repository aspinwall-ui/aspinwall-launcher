# coding: utf-8
"""Contains window creation code for the Aspinwall launcher"""
from gi import require_version as gi_require_version
gi_require_version("Gtk", "4.0")
gi_require_version('Adw', '1')
from gi.repository import Adw, Gtk, Gio
from pathlib import Path
import os
import time
import threading

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
	app_chooser_button_revealer = Gtk.Template.Child()

	focused = True
	pause_focus_manager = False

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

		# Set up idle mode

		# The motion controller is added/removed as needed, to avoid lag
		self.motion_controller = Gtk.EventControllerMotion.new()
		self.motion_controller.connect('motion', self.on_focus)

		self.click_controller = Gtk.GestureClick.new()
		self.click_controller.connect('pressed', self.on_focus)
		self.click_controller.connect('released', self.on_focus)
		self.add_controller(self.click_controller)

		self.focus_manager_thread = threading.Thread(target=self.focus_manager_loop, daemon=True)
		self.focus_manager_thread.start()

		config.connect('changed::idle-mode-delay', self.update_unfocus_countdown)

		self.connect('realize', self.on_realize)

	def on_realize(self, *args):
		surface = self.get_surface()
		surface.connect('notify::width', self.set_widgetbox_width)

	def set_widgetbox_width(self, *args):
		"""Sets the widgetbox's width to match 50% of the screen."""
		width_request = self.get_surface().get_width() / 2 - 40
		if width_request > 0:
			self.clockbox.set_size_request(width_request, 0)
			self.widgetbox.set_size_request(width_request, 0)
		else:
			self.clockbox.set_size_request(0, 0)
			self.widgetbox.set_size_request(0, 0)

	def show_app_chooser(self, *args):
		"""Shows the app chooser."""
		self.pause_focus_manager = True
		# Reload apps, clear search
		self.app_chooser.search.set_text('')
		self.app_chooser.update_model()
		# Show chooser
		self.launcher_flap.set_reveal_flap(True)
		self.app_chooser.search.grab_focus()

	def update_unfocus_countdown(self, *args):
		"""
		Used to update the unfocus countdown value whenever the setting
		changes.
		"""
		self.unfocus_countdown = config['idle-mode-delay'] + 1

	def focus_manager_loop(self):
		"""Loop that manages focused/unfocused mode. Run as a thread."""
		self.unfocus_countdown = config['idle-mode-delay'] + 1
		while True:
			if self.focused and not self.pause_focus_manager:
				self.unfocus_countdown -= 1
				if self.unfocus_countdown <= 0:
					self.on_unfocus()
			time.sleep(1)

	def on_unfocus(self, *args):
		"""Performs actions on unfocus."""
		if self.focused:
			self.focused = False
			self.unfocus_countdown = config['idle-mode-delay'] + 1
			self.app_chooser_button_revealer.set_reveal_child(False)
			self.widgetbox.chooser_button_revealer.set_reveal_child(False)
			self.launcher_flap.add_css_class('unfocused')
			self.add_controller(self.motion_controller)

	def on_focus(self, *args):
		"""Performs actions on focus."""
		if not self.focused:
			self.remove_controller(self.motion_controller)
			self.focused = True
			self.unfocus_countdown = config['idle-mode-delay'] + 1
			self.app_chooser_button_revealer.set_reveal_child(True)
			self.widgetbox.chooser_button_revealer.set_reveal_child(True)
			self.launcher_flap.remove_css_class('unfocused')
		else:
			self.unfocus_countdown = config['idle-mode-delay'] + 1

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
