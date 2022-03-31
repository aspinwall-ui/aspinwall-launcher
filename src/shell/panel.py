# coding: utf-8
"""
Contains the code for the panel.
"""
from gi.repository import Gtk, GObject

from aspinwall.shell.surface import Surface, SurfaceType
from aspinwall.utils.clock import clock_daemon
from aspinwall.shell.config import config
from aspinwall.shell.interfaces.manager import get_interface_manager

import time

@Gtk.Template(resource_path='/org/dithernet/aspinwall/shell/ui/panel.ui')
class Panel(Surface):
	"""The status bar on the top of the screen."""
	__gtype_name__ = 'Panel'

	clock = Gtk.Template.Child()
	status_icons_start = Gtk.Template.Child()
	status_icons_end = Gtk.Template.Child()

	battery_icon = Gtk.Template.Child()
	battery_percentage = Gtk.Template.Child()

	wifi_icon = Gtk.Template.Child()

	def __init__(self, app):
		"""Initializes the panel."""
		super().__init__(
			application=app,
			hexpand=True,
			height=36,
			focus_on_create=True,
			type=SurfaceType.DOCK
		)

		clock_daemon.connect('notify::time', self.update_time)
		self.clock.set_label(time.strftime('%H:%M'))

		# Set up status icons
		interface_manager = get_interface_manager()
		battery = interface_manager.get_interface_by_name('BatteryInterface')
		battery.bind_property('icon-name', self.battery_icon, 'icon-name',
			GObject.BindingFlags.SYNC_CREATE
		)

		network = interface_manager.get_interface_by_name('NetworkManagerInterface')
		network.bind_property('icon-name', self.wifi_icon, 'icon-name',
			GObject.BindingFlags.SYNC_CREATE
		)

		config.connect('changed::show-battery-percentage', self.toggle_battery_percentage)
		self.toggle_battery_percentage()

		# Set up swipe-to-show-control-panel
		swipe_gesture = Gtk.GestureSwipe.new()
		swipe_gesture.connect('swipe', self.swipe_handler)
		self.add_controller(swipe_gesture)

	def swipe_handler(self, handler, x, y, *args):
		"""Handles swipes on the panel."""
		if y > 0:
			from aspinwall.shell.control_panel import control_panel
			control_panel_revealer = control_panel.container_revealer

			panel_width = self.get_width()
			if panel_width <= 320:
				control_panel_revealer.set_halign(Gtk.Align.FILL)
			else:
				tapped_x = handler.get_point().x
				one_third_panel_width = panel_width / 3

				if tapped_x <= one_third_panel_width:
					control_panel_revealer.set_halign(Gtk.Align.START)
				elif tapped_x <= one_third_panel_width * 2:
					control_panel_revealer.set_halign(Gtk.Align.CENTER)
				else:
					control_panel_revealer.set_halign(Gtk.Align.END)

			control_panel.show_control_panel()

	def toggle_battery_percentage(self, *args):
		"""
		Toggles the battery percentage display on or off based on the
		config option.
		"""
		if config['show-battery-percentage']:
			self.battery_percentage.set_visible(True)
		else:
			self.battery_percentage.set_visible(False)

	def update_time(self, *args):
		"""Updates the time on the clock."""
		self.clock.set_label(time.strftime('%H:%M'))
