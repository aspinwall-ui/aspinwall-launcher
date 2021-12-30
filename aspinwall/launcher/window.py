# coding: utf-8
"""Contains window creation code for the Aspinwall launcher"""
import gi
gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Adw, Gtk, Gdk
import threading
import time
import os

from aspinwall.launcher.config import config
from aspinwall.launcher.widgets import AspWidget

@Gtk.Template(filename=os.path.join(os.path.dirname(__file__), 'ui', 'widgetbox.ui'))
class WidgetBox(Gtk.Box):
	"""Box that contains the widgets."""
	__gtype_name__ = 'WidgetBox'

	_widgets = []

	def __init__(self):
		"""Initializes the widget box."""
		super().__init__()

	def add(self, widget_class, config={}, position=-1):
		"""Adds a widget to the WidgetBox."""
		aspwidget = AspWidget(widget_class, config)
		self._widgets.insert(position, aspwidget)
		if position == -1:
			super().append(aspwidget)
		else:
			super().insert_child_after(aspwidget, self._widgets[position])

		self.save_widgets()

@Gtk.Template(filename=os.path.join(os.path.dirname(__file__), 'ui', 'clockbox.ui'))
class ClockBox(Gtk.Box):
	"""Box that contains the launcher's clock."""
	__gtype_name__ = 'ClockBox'

	clockbox_time = Gtk.Template.Child()
	clockbox_date = Gtk.Template.Child()

	def __init__(self):
		"""Initializes the clock box."""
		super().__init__()

		self._updater = threading.Thread(target=self.update, daemon=True)
		self._updater.start()

	def update(self):
		"""Updates the time and date on the clock."""
		while True:
			self.clockbox_time.set_markup('<span weight="bold" font="28">' + time.strftime("%X") + '</span>')
			self.clockbox_date.set_markup('<span font="22">' + time.strftime("%A, %x") + '</span>')
			time.sleep(1)

@Gtk.Template(filename=os.path.join(os.path.dirname(__file__), 'ui', 'launcher.ui'))
class Launcher(Gtk.ApplicationWindow):
	"""Base class for launcher window."""
	__gtype_name__ = 'Launcher'

	def __init__(self):
		"""Initializes the launcher window."""
		super().__init__(title='Aspinwall Launcher', application=app)

def on_activate(app):
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
