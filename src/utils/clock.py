# coding: utf-8
"""
Contains common code for clock management
"""
from gi.repository import GObject
import time
import threading

class ClockDaemon(GObject.Object):
	"""
	Provides accurate time data for portions of the shell that require it.

	Clients can hook up to the `notify::time` signal to recieve an update
	whenever the time updates.
	"""
	__gtype_name__ = 'ClockDaemon'

	def __init__(self):
		"""Initializes the clock daemon."""
		super().__init__()
		self.update_thread = threading.Thread(target=self.update_func, daemon=True)
		self.update_thread.start()

	def update_func(self):
		"""
		Infinite loop that updates the clock. This changes the self._time
		variable every second, which contains the time in the form of a
		number contains the amount of seconds from the Unix epoch.
		"""
		self.set_property('time', time.time())

		# Sync as close to 0th millisecond as possible
		start_time = time.time()
		time.sleep(1 - (time.time() % 1))

		start_time = time.time()
		while True:
			self.set_property('time', time.time())
			time.sleep(1.0 - ((time.time() - start_time) % 1.0))

	@GObject.Property
	def time(self):
		"""The currently stored time."""
		return self._time

	@time.setter
	def time(self, new_time):
		self._time = new_time

clock_daemon = ClockDaemon()
