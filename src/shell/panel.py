# coding: utf-8
"""
Contains the code for the panel.
"""
from gi.repository import Gtk

from aspinwall.shell.surface import Surface
from aspinwall.utils.clock import clock_daemon
import time

@Gtk.Template(resource_path='/org/dithernet/aspinwall/shell/ui/panel.ui')
class Panel(Surface):
	"""The status bar on the top of the screen."""
	__gtype_name__ = 'Panel'

	clock = Gtk.Template.Child()

	def __init__(self, app):
		"""Initializes the panel."""
		super().__init__(application=app, hexpand=True, height=32)
		clock_daemon.connect('notify::time', self.update_time)
		self.clock.set_label(time.strftime('%H:%M'))

	def update_time(self, *args):
		"""Updates the time on the clock."""
		self.clock.set_label(time.strftime('%H:%M'))
