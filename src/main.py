# coding: utf-8
"""Contains code for the Application object."""
from gi import require_version as gi_require_version
gi_require_version("Gtk", "4.0")
gi_require_version('Adw', '1')
import os

from gi.repository import Adw, Gtk
from .launcher.window import Launcher
from .config import config

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
	if config['available-wallpapers'] and config['available-wallpapers'][0] == 'fixme':
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

class Application(Adw.Application):
	def __init__(self, version='development'):
		super().__init__(application_id='org.dithernet.aspinwall.Launcher',
						 resource_base_path='/org/dithernet/aspinwall/launcher/stylesheet')
		self.version = version
		style_manager = self.get_style_manager()
		on_theme_preference_change()
		config.connect('changed::theme-preference', on_theme_preference_change)
		style_manager.connect('notify::color-scheme', on_theme_preference_change)

	def do_activate(self):
		win = self.props.active_window
		if not win:
			launcher_setup()
			win = Launcher(application=self, version=self.version)
		win.present()

		if 'GTK_DEBUG' not in os.environ or not os.environ['GTK_DEBUG']:
			win_surface = win.get_surface()
			win.set_size_request(win_surface.get_width(), win_surface.get_height())
			win.fullscreen()
		else:
			win.set_size_request(1270, 720)

def main(version):
	app = Application(version)
	return app.run()
