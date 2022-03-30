# coding: utf-8
"""
Contains the code for the panel.
"""
from gi import require_version as gi_require_version
gi_require_version("Gtk", "4.0")
gi_require_version('Adw', '1')

from gi.repository import Adw, Gtk
from aspinwall.shell.interfaces.manager import start_interface_manager

from aspinwall.shell.control_panel import ControlPanelContainer
from aspinwall.shell.notification_popup import NotificationPopup
from aspinwall.shell.window_switcher import WindowSwitcher
from aspinwall.shell.panel import Panel

running = False

class ShellManager:
	"""Main shell daemon class, keeps track of running windows."""
	def __init__(self, app):
		"""Initializes the shell."""
		# Initialize interfaces
		start_interface_manager()

		# Initialize shell surfaces
		self.windows = Gtk.WindowGroup()

		style_manager = Adw.StyleManager.get_default()
		style_manager.set_color_scheme(Adw.ColorScheme.FORCE_DARK)

		self.window_switcher = WindowSwitcher(app)
		self.windows.add_window(self.window_switcher)

		self.control_panel = ControlPanelContainer(app)
		self.windows.add_window(self.control_panel)

		self.notification_popup = NotificationPopup(app)
		self.windows.add_window(self.notification_popup)

		self.panel = Panel(app)
		self.windows.add_window(self.panel)

		self.panel.show()

		self.window_switcher.set_transient_for(self.panel)
		self.control_panel.set_transient_for(self.panel)
		self.notification_popup.set_transient_for(self.panel)
		self.panel.present()

def on_activate(app):
	global running
	if running:
		return False
	running = True

	global shell_manager
	shell_manager = ShellManager(app)

def main(version):
	global _version
	_version = version
	app = Adw.Application(application_id='org.dithernet.aspinwall.Shell')
	app.set_resource_base_path('/org/dithernet/aspinwall/stylesheet')
	app.connect('activate', on_activate)
	app.run()
