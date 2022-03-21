# coding: utf-8
"""
Contains code for notifications.
"""
from gi.repository import Adw, Gtk, GdkPixbuf, GObject
import os.path
from urllib.parse import urlparse

def image_data_to_dict(image_data):
	"""
	Converts a desktop notification image data array into a dict.
	"""
	result = {}

	result['width'] = image_data[0]
	result['height'] = image_data[1]
	result['rowstride'] = image_data[2]
	result['has_alpha'] = image_data[3]
	result['bits_per_sample'] = image_data[4]
	result['channels'] = image_data[5]
	result['data'] = image_data[6]

	return result

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

		if 'action-icons' in self.notification.props.hints:
			use_action_icons = self.notification.props.hints['action-icons']
		else:
			use_action_icons = False

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

	value_bar = Gtk.Template.Child()
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

		# Set up value bar
		if 'value' in notification.props.hints:
			self.value_bar.set_visible(True)
			self.value_bar.set_fraction(int(notification.props.hints['value']) / 100)

		# Set up icon
		hints = self.notification.props.hints
		self.icon.set_visible(True)

		if 'icon_data' in hints and hints['icon_data']:
			image_data = image_data_to_dict(hints['icon_data'])
		elif 'image-data' in hints and hints['image-data']:
			image_data = image_data_to_dict(hints['image-data'])
		else:
			image_data = None

		if 'image-path' in hints and hints['image-path']:
			image_path = hints['image-path']
		elif self.notification.props.app_icon:
			image_path = self.notification.props.app_icon
		else:
			image_path = None

		if image_data:
			pixbuf = GdkPixbuf.Pixbuf.new_from_data(
				image_data['data'], GdkPixbuf.Colorspace.RGB,
				image_data['has_alpha'],
				image_data['bits_per_sample'],
				image_data['width'], image_data['height'],
				image_data['rowstride']
			)
			self.icon.set_from_pixbuf(pixbuf)
		elif image_path:
			# Depending on the caller program, the image path may be provided
			# in one of three formats:
			#   * as an URI (starts with file://)
			#   * as a file path
			#   * as an icon name
			# Thus, we need to figure out which one is passed.

			if 'file://' in image_path:
				# Handle URI; this is safe, per the spec only file:// is supported
				parsed = urlparse(image_path)
				final_path = os.path.abspath(os.path.join(parsed.netloc, parsed.path))
			elif '/' in image_path or '\\' in image_path:
				# Handle local file path
				final_path = image_path
			else:
				# We're dealing with an icon name
				final_path = None
				self.icon.set_from_icon_name(image_path)

			if final_path:
				self.icon.set_from_file(final_path)
		else:
			# No icon
			self.icon.set_visible(False)

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
