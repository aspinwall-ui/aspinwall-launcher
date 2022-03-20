# coding: utf-8
"""
Contains code for notifications.
"""
from gi.repository import Gtk, GObject

@Gtk.Template(resource_path='/org/dithernet/aspinwall/shell/ui/notificationbox.ui')
class NotificationBox(Gtk.Revealer):
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

	notification = None

	_icon_name = None
	_title = None
	_description = None

	def __init__(self):
		super().__init__()

		# This is done when the widget is mapped so that the animation plays
		self.connect('map', self.show)

		self.connect('notify::child-revealed', self.dismiss)

		# Set up swipe-to-dismiss gesture
		self.swipe_gesture = Gtk.GestureSwipe.new()
		self.swipe_gesture.connect('swipe', self.handle_swipe)
		self.add_controller(self.swipe_gesture)

	def show(self, *args):
		"""Shows the notification."""
		self.set_reveal_child(True)

	def dismiss(self, *args):
		"""Dismisses the notification."""
		if self.get_child_revealed() is False:
			self.set_visible(False)
			self.notification.dismiss()

	def handle_swipe(self, gesture, x, y, *args):
		"""Handles a swipe gesture."""
		if x <= 20 and x >= -20:
			return
		elif x > 20:
			self.set_transition_type(Gtk.RevealerTransitionType.SLIDE_LEFT)
			self.set_transition_duration(200)
			self.set_reveal_child(False)
		else:
			self.set_transition_type(Gtk.RevealerTransitionType.SLIDE_RIGHT)
			self.set_transition_duration(200)
			self.set_reveal_child(False)

	def bind_to_notification(self, notification):
		"""
		Takes a Notification object and makes the NotificationBox
		show its values.
		"""
		self.set_property('icon_name', notification.app_icon)
		self.set_property('title', notification.summary)
		self.set_property('description', notification.body)
		self.notification = notification

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
