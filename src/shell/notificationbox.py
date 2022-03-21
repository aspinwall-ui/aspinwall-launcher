# coding: utf-8
"""
Contains code for notifications.
"""
from gi.repository import Adw, Gtk, Gio, GObject

from aspinwall.shell.interfaces.notification import Action

class ActionButton(Gtk.Button):
	"""Simple button representing an action."""
	__gtype_name__ = 'ActionButton'

	def __init__(self, notification):
		"""Sets up an ActionButton."""
		super().__init__()
		self.notification = notification

	def bind_to_action(self, action):
		"""Takes an Action object and applies its properties to the button."""
		self.action = action

		use_action_icons = self.notification.props.hints['action-icons']
		action_key = action.props.action
		label = action.props.label

		self.set_label(label)
		if use_action_icons and action_key != 'default':
			button_content = Adw.ButtonContent.new()
			button_content.set_icon_name(action_key)
			button_content.set_label(label)
			self.set_child(button_content)

		self.connect('clicked', self.invoke)

	def invoke(self, *args):
		"""Callback wrapper for Action.invoke."""
		self.action.invoke()

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

	action_buttons = Gtk.Template.Child()

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
		self.notification = notification

		self.set_property('icon_name', notification.app_icon)
		self.set_property('title', notification.summary)
		self.set_property('description', notification.body)

		# Set up action store
		action_factory = Gtk.SignalListItemFactory()
		action_factory.connect('setup', self.action_button_setup)
		action_factory.connect('bind', self.action_button_bind)

		self.action_buttons.set_model(Gtk.SingleSelection(
			model=self.notification.actions)
		)
		self.action_buttons.set_factory(action_factory)

	def action_button_setup(self, factory, item):
		item.set_child(ActionButton(self.notification))

	def action_button_bind(self, factory, item):
		action = item.get_item()
		button = item.get_child()
		button.bind_to_action(action)

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
