# coding: utf-8
"""Contains window creation code for the Aspinwall launcher"""
import gi
gi.require_version("Gtk", "4.0")
from gi.repository import Gtk, Gdk
import os

from aspinwall.launcher.config import config
from aspinwall.launcher.launcherboxes import ClockBox, WidgetBox
from aspinwall.widgets.loader import load_widgets

@Gtk.Template(filename=os.path.join(os.path.dirname(__file__), 'ui', 'launcher.ui'))
class Launcher(Gtk.ApplicationWindow):
	"""Base class for launcher window."""
	__gtype_name__ = 'Launcher'

	def __init__(self):
		"""Initializes the launcher window."""
		super().__init__(title='Aspinwall Launcher', application=app)

def on_activate(app):
	load_widgets()

	win = Launcher()
	style_provider = Gtk.CssProvider()
	style_provider.load_from_path(os.path.join(os.path.dirname(__file__), 'launcher.css'))

	Gtk.StyleContext.add_provider_for_display(
		Gdk.Display.get_default(),
		style_provider,
		Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
	)
	win.present()

def on_shutdown(app):
	config.save()

if __name__ == "__main__":
	app = Gtk.Application(application_id='org.dithernet.AspinwallLauncher')
	app.connect('activate', on_activate)
	app.connect('shutdown', on_shutdown)
	app.run()
