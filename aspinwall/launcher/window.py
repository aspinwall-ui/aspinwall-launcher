# coding: utf-8
"""Contains window creation code for the Aspinwall launcher"""
import gi
gi.require_version("Gtk", "4.0")
from gi.repository import Gtk, Gdk, GObject
import os

from aspinwall.launcher.config import config
from aspinwall.widgets.loader import load_widgets

# The ClockBox, WidgetBox and AppChooser classes are imported to avoid
# "invalid object type" errors.
from aspinwall.launcher.launcher_boxes import ClockBox, WidgetBox # noqa: F401
from aspinwall.launcher.app_chooser import AppChooser # noqa: F401

@Gtk.Template(filename=os.path.join(os.path.dirname(__file__), 'ui', 'launcher.ui'))
class Launcher(Gtk.ApplicationWindow):
	"""Base class for launcher window."""
	__gtype_name__ = 'Launcher'

	widgetbox = Gtk.Template.Child()
	app_chooser = Gtk.Template.Child()

	def __init__(self):
		"""Initializes the launcher window."""
		super().__init__(title='Aspinwall Launcher', application=app)
		self.app_chooser.set_transition_type(Gtk.RevealerTransitionType.SLIDE_RIGHT)

	@Gtk.Template.Callback()
	def show_app_chooser(self, *args):
		"""Shows the app chooser."""
		self.app_chooser.set_reveal_child(True)

def on_gtk_theme_change(settings, theme_name, theme_name_is_str, style_provider):
	"""Reloads the CSS provider as needed."""
	if settings.get_property('gtk-theme-name') in ('HighContrast', 'Default-hc'):
		stylesheet = 'default-hc.css'
	else:
		stylesheet = 'default-dark.css'

	style_provider.load_from_path(os.path.join(os.path.dirname(__file__), '..', 'stylesheet', stylesheet))

def on_activate(app):
	load_widgets()

	win = Launcher()

	gtk_settings = Gtk.Settings.get_default()
	gtk_settings.set_property('gtk-application-prefer-dark-theme', True)

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

def on_shutdown(app):
	config.save()

if __name__ == "__main__":
	app = Gtk.Application(application_id='org.dithernet.AspinwallLauncher')
	app.connect('activate', on_activate)
	app.connect('shutdown', on_shutdown)
	app.run()
