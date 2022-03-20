# coding: utf-8
"""
Notification handler and interface.
"""
from aspinwall.shell.interfaces import Interface
from gi.repository import Gio, GObject

import dbus
import dbus.service
from dbus.mainloop.glib import DBusGMainLoop
DBusGMainLoop(set_as_default=True)

BUS_NAME = 'org.freedesktop.Notifications'
BUS_PATH = '/org/freedesktop/Notifications'
BUS_INTERFACE_NAME = BUS_NAME

session_bus = dbus.SessionBus()
max_id = 0

class Notification(GObject.Object):
	"""
	GObject representation of a notification.
	"""
	__gtype_name__ = 'Notification'

	def __init__(self, app_name, replaces_id, app_icon, summary, body, actions,
				 hints, expire_timeout):
		"""Initializes the notification."""
		super().__init__()
		self._app_name = app_name
		self._replaces_id = replaces_id
		self._app_icon = app_icon
		self._summary = summary
		self._body = body
		self._actions = actions
		self._hints = hints
		self._expire_timeout = expire_timeout

		global max_id
		max_id += 1
		self._id = max_id

	@GObject.Property(type=str, flags=GObject.ParamFlags.READABLE)
	def id(self):
		"""The notification's ID."""
		return self._id

	@GObject.Property(type=str, flags=GObject.ParamFlags.READABLE)
	def app_name(self):
		"""Name of the application that sent the notification."""
		return self._app_name

	@GObject.Property(type=int, flags=GObject.ParamFlags.READABLE)
	def replaces_id(self):
		"""ID of notification that this notification replaces."""
		return self._app_name

	@GObject.Property(type=str, flags=GObject.ParamFlags.READABLE)
	def app_icon(self):
		"""Name of the app's icon."""
		return self._app_icon

	@GObject.Property(type=str, flags=GObject.ParamFlags.READABLE)
	def summary(self):
		"""Notification summary."""
		return self._summary

	@GObject.Property(type=str, flags=GObject.ParamFlags.READABLE)
	def body(self):
		"""Notification body."""
		return self._body

	@GObject.Property(flags=GObject.ParamFlags.READABLE)
	def actions(self):
		"""Notification actions."""
		return self._actions

	@GObject.Property(type=int, flags=GObject.ParamFlags.READABLE)
	def expire_timeout(self):
		"""Expire timeout."""
		return self._expire_timeout

class DBusNotificationDaemon(dbus.service.Object):
	"""DBus daemon for listening to notification messages."""

	def __init__(self, bus_name):
		super().__init__(bus_name, BUS_PATH)
		self.store = Gio.ListStore(item_type=Notification)

	@dbus.service.method(dbus_interface='org.freedesktop.Notifications',
		in_signature='', out_signature='ssss')
	def GetServerInformation(self):
		return ('dbus', 'Aspinwall', '0.1', '1.2')

	@dbus.service.method(dbus_interface='org.freedesktop.Notifications',
		in_signature='', out_signature='as')
	def GetCapabilities(self):
		return ['actions', 'body', 'body-hyperlinks', 'body-markup', 'icon-static', 'sound']

	@dbus.service.method(dbus_interface=BUS_INTERFACE_NAME,
						 in_signature='susssasa{sv}i', out_signature='u')
	def Notify(self, app_name, replaces_id, app_icon, summary, body, actions,
			   hints, expire_timeout):
		"""Main notification handler."""
		notification = Notification(
			app_name, replaces_id, app_icon, summary, body, actions, hints, expire_timeout
		)
		self.store.append(notification)
		return notification.id

class NotificationInterface(Interface):
	"""
	Interface for DBus notifications received over the
	org.freedesktop.Notifications bus.
	"""
	__gtype_name__ = 'NotificationInterface'

	def __init__(self):
		"""Initializes the notification interface."""
		super().__init__()
		try:
			bus_name = dbus.service.BusName(
				BUS_NAME, bus=session_bus, do_not_queue=True,
				allow_replacement=True, replace_existing=True
			)
		except dbus.exceptions.NameExistsException:
			self.set_property('available', False)
			return
		else:
			self.set_property('available', True)

		self.daemon = DBusNotificationDaemon(bus_name)

	@GObject.Property(flags=GObject.ParamFlags.READABLE)
	def notifications(self):
		"""Returns the notification daemon's notification store."""
		return self.daemon.store
