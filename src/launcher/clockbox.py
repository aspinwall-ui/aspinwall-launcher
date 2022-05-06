# coding: utf-8
"""
Contains code for the ClockBox. The clock refresh is handled by the clock
daemon (utils/clock.py).
"""
from gi.repository import Gtk
import time

from aspinwall.utils.clock import clock_daemon
from aspinwall.utils.dimmable import Dimmable
from aspinwall.launcher.config import config

@Gtk.Template(resource_path='/org/dithernet/aspinwall/launcher/ui/clockbox.ui')
class ClockBox(Gtk.Box, Dimmable):
	"""Box that contains the launcher's clock."""
	__gtype_name__ = 'ClockBox'

	clockbox_time = Gtk.Template.Child()
	clockbox_date = Gtk.Template.Child()

	def __init__(self):
		"""Initializes the clock box."""
		super().__init__()
		self.update_size()
		config.connect('changed::clock-size', self.update_size)
		clock_daemon.connect('notify::time', self.update)

	def update_size(self, *args):
		"""Updates the size of the clock based on the clock-size config."""
		size = config['clock-size']
		if size == 0:
			self.add_css_class('small')
			self.remove_css_class('medium')
			self.remove_css_class('large')
		elif size == 1:
			self.add_css_class('medium')
			self.remove_css_class('small')
			self.remove_css_class('large')
		elif size == 2:
			self.add_css_class('large')
			self.remove_css_class('small')
			self.remove_css_class('medium')

	def update(self, *args):
		"""Updates the time and date on the clock."""
		self.clockbox_time.set_markup(
			'<span weight="bold">' + time.strftime(config['time-format']) + '</span>'
		)
		self.clockbox_date.set_markup(
			'<span>' + time.strftime(config['date-format']) + '</span>'
		)
