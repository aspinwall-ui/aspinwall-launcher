# coding: utf-8
"""
The interfaces submodule contains interfaces to various APIs, all subclassed
from the Interface class.
"""
from gi.repository import GObject

class Interface(GObject.Object):
	"""
	Base class for interfaces.

	Properties:
	  - name - returns the interface name (equal to the gtype name of the
		       interface object).
	  - available - whether the interface is available or not.
	"""
	__gtype_name__ = 'Interface'

	_available = False
	_active = False

	def __init__(self):
		super().__init__()

	@GObject.Property(type=bool, default=False)
	def available(self):
		"""
		Whether the interface is available or not.

		Interfaces should set this to True if the backend APIs/libraries are
		available and enabled (for example - Wi-Fi library is available and
		we're not in airplane mode).
		"""
		return self._available

	@available.setter
	def set_available(self, available):
		"""Marks the interface as available/unavailable."""
		self._available = available

	@GObject.Property(type=bool, default=False)
	def active(self):
		"""
		Whether the interface is active or not.

		Interfaces should set this to True if the backend is "connected"
		(for example, when the user connects to a Wi-Fi network or Bluetooth
		device, or if something like NFC is disabled/enabled).
		"""
		return self._active

	@active.setter
	def set_active(self, active):
		"""Marks the interface as active/unactive."""
		self._active = active

	@GObject.Property(type=str, flags=GObject.ParamFlags.READABLE)
	def name(self):
		"""Name of the interface (this is equal to its gtype name)."""
		return self.__gtype_name__
