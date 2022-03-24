# coding: utf-8
"""
Contains code for the interface manager
"""
from aspinwall.shell.interfaces.battery import BatteryInterface
from aspinwall.shell.interfaces.notification import NotificationInterface
from aspinwall.shell.interfaces.pulseaudio import PulseAudioInterface

interface_manager = None

class InterfaceManager:
	"""
	Manager that initializes all interfaces.
	"""
	interfaces = [BatteryInterface, NotificationInterface, PulseAudioInterface]
	enabled_interfaces = {}
	available_interfaces = []

	def __init__(self):
		"""Initializes the interface manager."""
		for interface in self.interfaces:
			initialized_iface = interface()
			self.enabled_interfaces[initialized_iface.props.name] = initialized_iface
			initialized_iface.connect('notify::available', self.set_availability)
			self.set_availability(interface)

	def get_interface_by_name(self, name):
		"""
		Returns an interface by its name, or None if the interface isn't loaded.
		"""
		try:
			return self.enabled_interfaces[name]
		except KeyError:
			return None

	def set_availability(self, interface, *args):
		"""Adds/removes the interface to the available interface list."""
		if interface.available and interface not in self.available_interfaces:
			self.available_interfaces.append(interface)
		elif interface in self.available_interfaces:
			self.available_interfaces.remove(interface)

def get_interface_manager():
	"""Returns the currently running interface manager."""
	global interface_manager
	return interface_manager

def start_interface_manager():
	"""
	Starts the interface manager. Returns the created manager, or False if
	it's already running.
	"""
	global interface_manager
	if interface_manager:
		print("Interface manager already running")
		return False

	interface_manager = InterfaceManager()
	return interface_manager
