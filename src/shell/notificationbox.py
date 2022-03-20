# coding: utf-8
"""
Contains code for notifications.
"""
from gi.repository import Gtk, GObject

@Gtk.Template(resource_path='/org/dithernet/aspinwall/shell/ui/notificationbox.ui')
class NotificationBox(Gtk.Box):
	"""
	Box containing a notification.

	Properties:
	  - icon_name - icon to use for the notification.
	  - title - notification title.
	  - description - notification description.
	"""
	__gtype_name__ = 'NotificationBox'

	icon = Gtk.Template.Child()
	title_label = Gtk.Template.Child()
	description_label = Gtk.Template.Child()

	_icon_name = None
	_title = None
	_description = None

	def __init__(self):
		super().__init__()

	def bind_to_notification(self, notification):
		"""
		Takes a Notification object and makes the NotificationBox
		show its values.
		"""
		self.set_property('icon_name', notification.app_icon)
		self.set_property('title', notification.summary)
		self.set_property('description', notification.body)

	@GObject.Property(type=str)
	def icon_name(self):
		"""Icon to use for the notification."""
		return self._icon_name

	@icon_name.setter
	def set_icon_name(self, icon_name):
		"""Sets a new icon name for the icon in the notification."""
		self._icon_name = icon_name
		self.icon.set_from_icon_name(icon_name)

	@GObject.Property(type=str)
	def title(self):
		"""Notification title."""
		return self._title

	@title.setter
	def set_title(self, title):
		"""Sets the notification title."""
		self._title = title
		self.title_label.set_label(title)

	@GObject.Property(type=str)
	def description(self):
		"""Notification description."""
		return self._description

	@description.setter
	def set_description(self, description):
		"""Sets the notification description."""
		self._description = description
		self.description_label.set_label(description)