# coding: utf-8
"""
Contains code for the control panel that appears after dragging the panel.
"""
from gi.repository import Adw, Gtk, GObject

from aspinwall.shell.surface import Surface
from aspinwall.shell.notificationbox import NotificationBox # noqa: F401
from aspinwall.utils.clock import clock_daemon

from aspinwall.shell.interfaces.manager import get_interface_manager

import time

control_panel = None

@Gtk.Template(resource_path='/org/dithernet/aspinwall/shell/ui/controlpanelbutton.ui')
class ControlPanelButton(Gtk.FlowBoxChild):
	"""
	Button for the control panel.

	Properties:
	  - icon_name - the name of the icon to use for the button.
	  - icon_label - the label to display under the button.
	  - icon_active - whether the icon is active or not.

	Functions:
	  - make_active() - makes the button active.
	  - make_inactive() - makes the button inactive.

	Signals:
	  - icon-clicked - emitted when the button in the icon is clicked.
	"""
	__gtype_name__ = 'ControlPanelButton'

	action_button = Gtk.Template.Child()
	action_button_icon = Gtk.Template.Child()
	action_label = Gtk.Template.Child()

	_icon_label = 'Unknown'
	_icon_name = 'system-preferences-symbolic'
	_icon_active = False

	def __init__(self, icon_name=None, icon_label=None, icon_active=None):
		"""Initializes the control panel icon."""
		super().__init__()
		if icon_name:
			self.set_icon_name(icon_name)
		if icon_label:
			self.set_icon_label(icon_label)
		if icon_active:
			self.set_icon_active(icon_active)
		self.action_button.connect('clicked', self.emit_icon_clicked)

	def bind_to_interface(self, interface):
		"""Binds the button to an interface."""
		self.set_sensitive(interface.available)
		self.set_icon_active(interface.active)
		self.bind_property('sensitive', interface, 'available')
		self.bind_property('icon-active', interface, 'active')

	def emit_icon_clicked(self, *args):
		"""Emits the icon-clicked signal. Used by the action button."""
		self.emit('icon-clicked')

	@GObject.Property(type=str)
	def icon_name(self):
		"""The icon name for the control panel icon."""
		return self._icon_name

	@icon_name.setter
	def set_icon_name(self, icon_name):
		"""Sets the icon name for the control panel icon."""
		self._icon_name = icon_name
		self.action_button_icon.set_from_icon_name(icon_name)

	@GObject.Property(type=str)
	def icon_label(self):
		"""The icon label for the control panel icon."""
		return self._icon_label

	@icon_label.setter
	def set_icon_label(self, icon_label):
		"""Sets the icon label for the control panel icon."""
		self._icon_label = icon_label
		self.action_label.set_label(icon_label)

	@GObject.Property(type=bool, default=False)
	def icon_active(self):
		"""Whether the icon should be marked as active or not."""
		return self._icon_active

	@icon_active.setter
	def set_icon_active(self, icon_active):
		"""Sets the icon active for the control panel icon."""
		self._icon_active = icon_active
		if icon_active:
			self.action_button.add_css_class('active')
		else:
			self.action_button.remove_css_class('active')

	@GObject.Signal
	def icon_clicked(self, *args):
		"""Emitted when the button in the icon is clicked."""
		pass

	def make_active(self, *args):
		"""Convenience function that makes the button active."""
		self.set_property('icon_active', True)

	def make_inactive(self, *args):
		"""Convenience function that makes the button inactive."""
		self.set_property('icon_active', False)

@Gtk.Template(resource_path='/org/dithernet/aspinwall/shell/ui/controlpanelcontainer.ui')
class ControlPanelContainer(Surface):
	"""
	Container for the control panel.
	"""
	__gtype_name__ = 'ControlPanelContainer'

	container = Gtk.Template.Child()
	container_bg = Gtk.Template.Child()
	container_revealer = Gtk.Template.Child()
	control_panel = Gtk.Template.Child()

	def __init__(self, application):
		"""Initializes the control panel container."""
		super().__init__(
			application=application,
			valign=Gtk.Align.START,
			hexpand=True,
			vexpand=True
		)

		global control_panel
		control_panel = self

		self.container_revealer.connect('notify::child-revealed', self.change_visibility)

		# Add clickaway gesture for the background behind the panel
		clickaway_gesture = Gtk.GestureClick.new()
		clickaway_gesture.connect('pressed', self.hide_control_panel)
		self.container_bg.add_controller(clickaway_gesture)

		self.connect('map', self.set_size)
		self.set_size()

	def set_size(self, *args):
		"""Sets/unsets margins and control panel size based on screen width"""
		width = self.surface_width
		height = self.surface_height
		if width > 480:
			self.control_panel.set_halign(Gtk.Align.END)
			self.control_panel.set_size_request(width / 3, 48)
			notif_list = self.control_panel.notification_list_scrollable
			notif_list.set_max_content_height(height / 2)
			self.container_revealer.set_margin_start(50)
			self.container_revealer.set_margin_end(50)
		else:
			self.control_panel.set_halign(Gtk.Align.CENTER)
			self.control_panel.set_size_request(width, 48)
			notif_list = self.control_panel.notification_list_scrollable
			notif_list.set_max_content_height(height - 300)
			self.container_revealer.set_margin_start(0)
			self.container_revealer.set_margin_end(0)

	def fadeout_worker(self, value, *args):
		"""Used by the background fadeout animation."""
		self.container_bg.set_opacity(value)

	def show_control_panel(self, *args):
		"""Shows the control panel."""
		self.set_visible(True)
		self.container.set_visible(True)
		self.container_revealer.set_reveal_child(True)

		# Fade in background
		anim = Adw.TimedAnimation.new(
			self,
			0, 1, 250,
			Adw.CallbackAnimationTarget.new(self.fadeout_worker)
		)
		anim.play()

	def hide_control_panel(self, *args):
		"""Hides the control panel."""
		self.container_revealer.set_reveal_child(False)

		# Fade out background
		anim = Adw.TimedAnimation.new(
			self,
			1, 0, 250,
			Adw.CallbackAnimationTarget.new(self.fadeout_worker)
		)
		anim.play()

	def change_visibility(self, *args):
		"""Sets the container visibility based on reveal progress."""
		progress = self.container_revealer.get_child_revealed()
		if progress:
			self.set_visible(True)
		else:
			self.set_visible(False)

@Gtk.Template(resource_path='/org/dithernet/aspinwall/shell/ui/controlpanel.ui')
class ControlPanel(Gtk.Box):
	"""
	The control panel that appears after dragging the top panel.
	"""
	__gtype_name__ = 'ControlPanel'

	clock_time = Gtk.Template.Child()
	clock_date = Gtk.Template.Child()

	no_notifications_revealer = Gtk.Template.Child()
	notification_list = Gtk.Template.Child()
	notification_list_scrollable = Gtk.Template.Child()

	def __init__(self):
		"""Initializes the control panel."""
		super().__init__()
		self.interface_manager = get_interface_manager()
		self.notification_interface = \
			self.interface_manager.get_interface_by_name('NotificationInterface')
		self.notification_store = self.notification_interface.props.notifications

		clock_daemon.connect('notify::time', self.update_time)
		self.update_time()

		notification_factory = Gtk.SignalListItemFactory()
		notification_factory.connect('setup', self.notification_setup)
		notification_factory.connect('bind', self.notification_bind)

		self.notification_list.set_model(Gtk.SingleSelection(
			model=self.notification_store)
		)
		self.notification_list.set_factory(notification_factory)

		self.notification_store.connect('items-changed', self.show_no_notifications)
		self.show_no_notifications()

	def show_no_notifications(self, *args):
		"""
		Shows/hides the "no notifications" text based on the amount of items
		in the notification store.
		"""
		if self.notification_store.get_n_items() > 0:
			self.no_notifications_revealer.set_reveal_child(False)
			self.notification_list_scrollable.set_visible(True)
		else:
			self.no_notifications_revealer.set_reveal_child(True)
			self.notification_list_scrollable.set_visible(False)

	def notification_setup(self, factory, list_item):
		list_item.set_child(NotificationBox())

	def notification_bind(self, factory, list_item):
		box = list_item.get_child()
		item = list_item.get_item()
		box.bind_to_notification(item)

	def update_time(self, *args):
		"""Updates the clock in the control panel."""
		self.clock_time.set_label(time.strftime('%H:%M'))
		self.clock_date.set_label(time.strftime('%x'))
