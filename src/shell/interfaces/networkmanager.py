# coding: utf-8
"""
Contains code for the NetworkManager interface.
"""
from gi.repository import GObject
import dbus
from dbus.mainloop.glib import DBusGMainLoop
DBusGMainLoop(set_as_default=True)

from aspinwall.shell.interfaces import Interface

system_bus = dbus.SystemBus()

class NetworkManagerInterface(Interface):
	"""
	NetworkManager interface. Provides information about the currently
	connected network and its signal.
	"""
	__gtype_name__ = 'NetworkManagerInterface'

	_icon_name = 'network-wireless-offline-symbolic'
	_active_connection = None
	_active_connection_settings = None

	def __init__(self):
		"""Sets up the NetworkManager interface."""
		super().__init__()
		try:
			self.proxy = system_bus.get_object(
				'org.freedesktop.NetworkManager',
				'/org/freedesktop/NetworkManager'
			)
			self.props_interface = dbus.Interface(
				self.proxy, 'org.freedesktop.DBus.Properties'
			)

			system_bus.add_signal_receiver(
				self.signal_handler,
				dbus_interface='org.freedesktop.DBus.Properties',
				path_keyword='path'
			)
		except:
			self.set_property('available', False)
			return
		else:
			self.set_property('available', True)

		self.update_active_connection()
		self.update_icon_name()

	def enable(self):
		"""Enables the network connection."""
		raise NotImplementedError
		# NetworkManager.NetworkManager.WirelessEnabled = True
		# self.set_property('active', True)

	def disable(self):
		"""Disables the network connection."""
		raise NotImplementedError
		# NetworkManager.NetworkManager.WirelessEnabled = False
		# self.set_property('active', False)

	def signal_handler(self, *args, path):
		"""Generic signal handler for the NetworkManager bus."""
		if '/org/freedesktop/NetworkManager/AccessPoint' in path:
			data = args[1]
			if 'Strength' in dict(data).keys():
				self.update_icon_name()

	@GObject.Property(type=str, flags=GObject.ParamFlags.READABLE)
	def icon_name(self):
		"""Returns the appropriate icon representing the network signal."""
		return self._icon_name

	@GObject.Property(flags=GObject.ParamFlags.READABLE)
	def active_connection(self):
		"""The active connection."""
		return self._active_connection

	@GObject.Property(flags=GObject.ParamFlags.READABLE)
	def active_connection_settings(self):
		"""The active connection's settings."""
		return self._active_connection_settings

	@GObject.Property(flags=GObject.ParamFlags.READABLE)
	def active_ap(self):
		"""The active access point."""
		return self._active_ap

	def update_active_connection(self):
		"""Updates the active connection."""
		active_connections = self.props_interface.Get(
			"org.freedesktop.NetworkManager",
			"ActiveConnections"
		)

		if active_connections:
			# There can be multiple active connections, but we can only
			# display one. Get rid of non-WiFi connections, and get the
			# first best network.

			for conn in active_connections:
				conn_proxy = system_bus.get_object('org.freedesktop.NetworkManager', conn)
				conn_props = dbus.Interface(conn_proxy, 'org.freedesktop.DBus.Properties')

				conn_path = conn_props.Get(
					'org.freedesktop.NetworkManager.Connection.Active',
					'Connection'
				)
				conn_object_proxy = system_bus.get_object(
					'org.freedesktop.NetworkManager', conn_path
				)
				connection = dbus.Interface(conn_object_proxy,
					'org.freedesktop.NetworkManager.Settings.Connection'
				)

				settings = connection.GetSettings()

				if not settings['connection']['type'] == '802-11-wireless':
					continue

				self._active_connection = conn_object_proxy
				self._active_connection_settings = connection
				self.notify('active-connection')
				self.notify('active-connection-settings')
				break

			# Get the active access point
			devices = conn_props.Get(
				'org.freedesktop.NetworkManager.Connection.Active',
				'Devices'
			)
			proxy = system_bus.get_object('org.freedesktop.NetworkManager',
				devices[0]
			)
			props = dbus.Interface(proxy, 'org.freedesktop.DBus.Properties')
			active_ap_path = props.Get(
				"org.freedesktop.NetworkManager.Device.Wireless", "ActiveAccessPoint"
			)
			if active_ap_path == '/':
				self._active_ap = None
			else:
				self._active_ap = system_bus.get_object('org.freedesktop.NetworkManager',
					active_ap_path
				)
			self.notify('active-ap')

		if self.props.active_connection:
			self.set_property('active', True)
		else:
			self.set_property('active', False)

	def update_icon_name(self):
		"""Sets up the strength icon."""
		connection = self.props.active_connection
		if connection:
			access_point = self.props.active_ap
			ap_props = dbus.Interface(access_point, "org.freedesktop.DBus.Properties")
			strength = int(ap_props.Get(
				'org.freedesktop.NetworkManager.AccessPoint',
				'Strength'
			))

			if strength >= 85:
				self._icon_name = 'network-wireless-signal-excellent-symbolic'
			elif strength >= 65:
				self._icon_name = 'network-wireless-signal-good-symbolic'
			elif strength >= 45:
				self._icon_name = 'network-wireless-signal-ok-symbolic'
			elif strength >= 15:
				self._icon_name = 'network-wireless-signal-weak-symbolic'
			else:
				self._icon_name = 'network-wireless-signal-none-symbolic'
		else:
			# if self.props.connecting:
			# 	self._icon_name = 'network-wireless-acquiring-symbolic'
			self._icon_name = 'network-wireless-offline-symbolic'

		self.notify('icon-name')
