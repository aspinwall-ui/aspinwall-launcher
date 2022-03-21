# coding: utf-8
"""
Notification handler and interface.
"""
from aspinwall.shell.interfaces import Interface
from gi.repository import Gio, Gtk, GObject
import threading
import time

import dbus
import dbus.service
from dbus.mainloop.glib import DBusGMainLoop
DBusGMainLoop(set_as_default=True)

BUS_NAME = 'org.freedesktop.Notifications'
BUS_PATH = '/org/freedesktop/Notifications'
BUS_INTERFACE_NAME = BUS_NAME

session_bus = dbus.SessionBus()
max_id = 0

class Action(GObject.Object):
	"""
	GObject representation of a notification action.
	"""
	__gtype_name__ = 'Action'

	def __init__(self, notification, action, label):
		"""Sets up an action."""
		super().__init__()
		self.notification = notification
		self._action = action
		self._label = label

	def invoke(self):
		"""Invokes the action."""
		self.notification.daemon.ActionInvoked(self.notification.id, self.action)

	@GObject.Property(type=str, flags=GObject.ParamFlags.READABLE)
	def action(self):
		"""The action key."""
		return self._action

	@GObject.Property(type=str, flags=GObject.ParamFlags.READABLE)
	def label(self):
		"""The action label."""
		return self._label

class Notification(GObject.Object):
	"""
	GObject representation of a notification.
	"""
	__gtype_name__ = 'Notification'

	dismissed = False

	def __init__(self, app_name, replaces_id, app_icon, summary, body, actions,
				 hints, expire_timeout, daemon):
		"""Initializes the notification."""
		super().__init__()
		self._time_received = time.time()
		self._app_name = app_name
		self._replaces_id = replaces_id
		self._app_icon = app_icon
		self._summary = summary
		self._body = body
		self._actions_list = actions
		self._hints = hints
		self._expire_timeout = expire_timeout

		if 'urgency' in hints and hints['urgency']:
			self._urgency = int(hints['urgency'])
		else:
			self._urgency = 1 # Normal

		self.daemon = daemon

		# Format action list for store
		self.actions = Gio.ListStore(item_type=Action)
		if actions:
			for action, label in zip(actions[::2], actions[1::2]):
				action = Action(self, str(action), str(label))
				self.actions.append(action)

		if expire_timeout >= 0:
			self.autoexpire = threading.Thread(target=self.do_autoexpire, daemon=True)
			self.autoexpire.start()

		if replaces_id:
			self.daemon.CloseNotification(replaces_id)

		global max_id
		max_id += 1
		self._id = max_id

	def do_autoexpire(self):
		"""
		Automatically dismisses the notificaton after the expiration timeout.
		"""
		time.sleep(self.props.expire_timeout / 1000)
		if not self.dismissed:
			self.dismiss(reason=1)

	def dismiss(self, reason=2):
		"""Dismisses the notification."""
		self.dismissed = True
		self.daemon.NotificationClosed(self.id, reason)

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
	def hints(self):
		"""Notification hints."""
		return self._hints

	@GObject.Property(type=int, flags=GObject.ParamFlags.READABLE)
	def expire_timeout(self):
		"""Expire timeout."""
		return self._expire_timeout

	@GObject.Property(type=int, flags=GObject.ParamFlags.READABLE)
	def time_received(self):
		"""The time when the notification was received by the daemon."""
		return self._time_received

	@GObject.Property(type=int, flags=GObject.ParamFlags.READABLE)
	def urgency(self):
		"""The notification's urgency."""
		return self._urgency

class DBusNotificationDaemon(dbus.service.Object):
	"""DBus daemon for listening to notification messages."""

	def __init__(self, bus_name):
		super().__init__(bus_name, BUS_PATH)
		self.dict = {}
		self.store = Gio.ListStore(item_type=Notification)

		self.sorter = Gtk.CustomSorter.new(self.notification_sort_func, None)
		self.sorted_store = Gtk.SortListModel(model=self.store)
		self.sorted_store.set_sorter(self.sorter)

	def notification_sort_func(self, a, b, *args):
		"""
		Custom sorter for notifications. Prioritizes newer notifications
		with a higher urgency.
		"""
		urgency = 0
		if a.props.time_received > b.props.time_received:
			urgency -= 1
		elif a.props.time_received < b.props.time_received:
			urgency += 1

		if a.props.urgency > b.props.urgency:
			urgency -= 2
		elif a.props.urgency < b.props.urgency:
			urgency += 2

		return urgency

	@dbus.service.method(dbus_interface=BUS_INTERFACE_NAME,
		in_signature='', out_signature='ssss')
	def GetServerInformation(self):
		return ('aspinwall-shell', 'Aspinwall', '0.1.0', '1.2')

	@dbus.service.method(dbus_interface=BUS_INTERFACE_NAME,
		in_signature='', out_signature='as')
	def GetCapabilities(self):
		return [
			'action-icons', 'actions', 'body', 'body-hyperlinks',
			'body-markup', 'icon-static', 'persistent'
		]

	@dbus.service.method(dbus_interface=BUS_INTERFACE_NAME,
						 in_signature='susssasa{sv}i', out_signature='u')
	def Notify(self, app_name, replaces_id, app_icon, summary, body, actions,
			   hints, expire_timeout):
		"""Main notification handler."""
		notification = Notification(
			app_name, replaces_id, app_icon, summary, body, actions, hints, expire_timeout,
			self
		)
		self.dict[notification.id] = notification
		self.store.append(notification)
		self.sorter.changed(Gtk.SorterChange.DIFFERENT)

		return notification.id

	@dbus.service.method(dbus_interface=BUS_INTERFACE_NAME,
						 in_signature='u')
	def CloseNotification(self, id):
		"""Dismisses the notification with the given ID."""
		self.NotificationClosed(id, 3)

	@dbus.service.signal(dbus_interface=BUS_INTERFACE_NAME,
						 signature='uu')
	def NotificationClosed(self, id, reason):
		"""Dismisses the notification with the given ID."""
		# Don't try to remove notification if it doesn't exist
		if id in self.dict.keys():
			self.dict[id].dismissed = True
			self.store.remove(self.store.find(self.dict[id])[1])
			self.dict.pop(id)
			self.sorter.changed(Gtk.SorterChange.DIFFERENT)

	@dbus.service.signal(dbus_interface=BUS_INTERFACE_NAME,
						 signature='us')
	def ActionInvoked(self, id, action_key):
		"""Invokes an action on the notification."""
		# Clients perform the action when they receive the signal;
		# we don't need to do anything extra to accomodate this.
		pass

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

	@GObject.Property(flags=GObject.ParamFlags.READABLE)
	def notifications_sorted(self):
		"""Returns the notification daemon's sorted notification store."""
		return self.daemon.sorted_store
