# coding: utf-8
"""
Interface for accessing battery data with psutil
"""
from gi.repository import GObject
import psutil
import threading
import time

from aspinwall.shell.interfaces import Interface

class BatteryInterface(Interface):
	"""
	Interface for accessing battery data with psutil.

	Properties:
	  - percentage - the battery percentage as an integer.
	  - charging - whether the battery is charging or not.
	  - icon-name - the icon representing the current battery state.
	"""
	__gtype_name__ = 'BatteryInterface'

	_percentage = 0
	_charging = False
	_icon_name = 'battery-missing-symbolic'

	def __init__(self):
		"""Initializes the battery interface."""
		super().__init__()
		battery = psutil.sensors_battery()
		if battery:
			self.update_daemon = threading.Thread(target=self.update_loop, daemon=True)
			self.update_daemon.start()
			self.set_property('available', True)
		else:
			self.set_property('available', False)

	def update(self, *args):
		"""Updates the interface with the latest data."""
		battery = psutil.sensors_battery()
		if not battery:
			# No battery. Bail out.
			self.set_property('available', False)
			self._icon_name = 'battery-missing-symbolic'
			self.notify('icon_name')
			return
		else:
			self.set_property('available', True)

			self._charging = battery.plugged
			self.notify('charging')

			self._percentage = int(battery.percentage)
			self.notify('percentage')

			if self._percentage >= 85:
				self._icon_name = 'battery-full'
			elif self._percentage >= 50:
				self._icon_name = 'battery-good'
			elif self._percentage >= 25:
				self._icon_name = 'battery-low'
			elif self._percentage >= 5:
				self._icon_name = 'battery-caution'
			else:
				self._icon_name = 'battery-empty'

			if self._charging:
				if self._percentage == 100:
					self._icon_name += '-charged'
				else:
					self._icon_name += '-charging'

			self._icon_name += '-symbolic'
			self.notify('icon-name')

	def update_loop(self, *args):
		while True:
			self.update()
			time.sleep(1)

	@GObject.Property(type=int, flags=GObject.ParamFlags.READABLE, default=0)
	def percentage(self):
		"""The battery percentage as an integer."""
		return self._percentage

	@GObject.Property(type=bool, flags=GObject.ParamFlags.READABLE, default=False)
	def charging(self):
		"""Whether the battery is charging or not."""
		return self._charging

	@GObject.Property(type=str, flags=GObject.ParamFlags.READABLE, default='battery-missing-symbolic')
	def icon_name(self):
		"""Name of an icon representing the current battery state."""
		return self._icon_name
