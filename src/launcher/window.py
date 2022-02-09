# coding: utf-8
"""Contains window creation code for the Aspinwall launcher"""
import gi
gi.require_version("Gtk", "4.0")
gi.require_version('Adw', '1')
from gi.repository import Adw, Gtk, Gdk, GObject
import os

from aspinwall.launcher.config import config
from aspinwall.widgets.loader import load_widgets

# The ClockBox, WidgetBox and AppChooser classes are imported to avoid
# "invalid object type" errors.
from aspinwall.launcher.launcher_boxes import ClockBox, WidgetBox # noqa: F401
from aspinwall.launcher.app_chooser import AppChooser # noqa: F401
from aspinwall.launcher.wallpaper import Wallpaper # noqa: F401

@Gtk.Template(resource_path='/org/dithernet/aspinwall/launcher/ui/launcher.ui')
class Launcher(Gtk.ApplicationWindow):
	"""Base class for launcher window."""
	__gtype_name__ = 'Launcher'

	widgetbox = Gtk.Template.Child()
	launcher_wallpaper_overlay = Gtk.Template.Child()
	wallpaper = Gtk.Template.Child('launcher_wallpaper')
	launcher_flap = Gtk.Template.Child()
	app_chooser = Gtk.Template.Child()

	def __init__(self, app):
		"""Initializes the launcher window."""
		super().__init__(title='Aspinwall Launcher', application=app)
		self.launcher_wallpaper_overlay.set_measure_overlay(self.launcher_flap, True)

	@Gtk.Template.Callback()
	def show_app_chooser(self, *args):
		"""Shows the app chooser."""
		# Reload apps, clear search
		self.app_chooser.update_model()
		self.app_chooser.search.set_text('')
		# Show chooser
		self.launcher_flap.set_reveal_flap(True)
		self.app_chooser.search.grab_focus()

def on_gtk_theme_change(settings, theme_name, theme_name_is_str, style_provider):
	"""Reloads the CSS provider as needed."""
	if settings.get_property('gtk-theme-name') in ('HighContrast', 'Default-hc'):
		stylesheet = 'default-hc.css'
	else:
		stylesheet = 'default-dark.css'

	style_provider.load_from_resource('/org/dithernet/aspinwall/stylesheet/' + stylesheet)

def on_activate(app):
	load_widgets()

	win = Launcher(app)

	gtk_settings = Gtk.Settings.get_default()

	style_provider = Gtk.CssProvider()
	Gtk.StyleContext.add_provider_for_display(
		Gdk.Display.get_default(),
		style_provider,
		Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
	)

	on_gtk_theme_change(gtk_settings, gtk_settings.get_property('gtk-theme-name'), True, style_provider)
	gtk_settings.connect('notify::gtk-theme-name', on_gtk_theme_change, False, style_provider)

	win.add_action(win.widgetbox._show_chooser_action)

	win.present()

	if not 'GTK_DEBUG' in os.environ or not os.environ['GTK_DEBUG']:
		win_surface = win.get_surface()
		win.set_size_request(win_surface.get_width(), win_surface.get_height())
		win.fullscreen()

def main(version):
	app = Adw.Application(application_id='org.dithernet.aspinwall.Launcher')
	app.connect('activate', on_activate)
	app.run()
