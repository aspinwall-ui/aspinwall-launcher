# coding: utf-8
"""
Contains code for the control panel that appears after dragging the panel.
"""
from gi.repository import Adw, Gdk, Gtk

from aspinwall.shell.surface import Surface

control_panel = None

@Gtk.Template(resource_path='/org/dithernet/aspinwall/shell/ui/controlpanelcontainer.ui')
class ControlPanelContainer(Surface):
	"""
	Container for the control panel.
	"""
	__gtype_name__ = 'ControlPanelContainer'

	container = Gtk.Template.Child()
	container_bg = Gtk.Template.Child()
	container_revealer = Gtk.Template.Child()

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

		clickaway_gesture = Gtk.GestureClick.new()
		clickaway_gesture.connect('pressed', self.hide_control_panel)
		self.container_bg.add_controller(clickaway_gesture)

	def fadeout_worker(self, value, *args):
		"""Used by the background fadeout animation."""
		self.container_bg.set_opacity(value)

	def show_control_panel(self, *args):
		"""Shows the control panel."""
		self.set_visible(True)
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
			self.container.set_visible(True)
		else:
			self.set_visible(False)
			self.container.set_visible(False)

@Gtk.Template(resource_path='/org/dithernet/aspinwall/shell/ui/controlpanel.ui')
class ControlPanel(Gtk.Box):
	"""
	The control panel that appears after dragging the top panel.
	"""
	__gtype_name__ = 'ControlPanel'

	def __init__(self):
		"""Initializes the control panel."""
		super().__init__()

		self.connect('map', self.set_size)

	def set_size(self, *args):
		"""Sets the size for the control panel."""
		monitor = Gdk.Display.get_default().get_monitor_at_surface(
			self.get_native().get_surface()
		)
		width = monitor.get_geometry().width
		if width > 400:
			self.set_halign(Gtk.Align.END)
			self.set_size_request(width / 3, 48)
		else:
			self.set_halign(Gtk.Align.CENTER)
			self.set_size_request(320, 48)
