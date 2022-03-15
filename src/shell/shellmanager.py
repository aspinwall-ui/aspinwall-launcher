# coding: utf-8
"""
Contains the code for the panel.
"""
from gi import require_version as gi_require_version
gi_require_version("Gtk", "4.0")
gi_require_version('Adw', '1')

from gi.repository import Adw, Gtk
from aspinwall.shell.control_panel import ControlPanelContainer
from aspinwall.shell.panel import Panel

running = False

class ShellManager:
	"""Main shell daemon class, keeps track of running windows."""
	def __init__(self, app):
		"""Initializes the shell."""
		self.windows = Gtk.WindowGroup()

		style_manager = Adw.StyleManager.get_default()
		style_manager.set_color_scheme(Adw.ColorScheme.FORCE_DARK)

		self.control_panel = ControlPanelContainer(app)
		self.windows.add_window(self.control_panel)

		self.panel = Panel(app)
		self.windows.add_window(self.panel)

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
