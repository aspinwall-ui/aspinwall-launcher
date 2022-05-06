# coding: utf-8
"""
Contains code for the ClockBox and WidgetBox.
"""
from gi.repository import Adw, GLib, Gtk, Gio
import threading
import time
import uuid

from aspinwall.utils.clock import clock_daemon
from aspinwall.utils.dimmable import Dimmable
from aspinwall.launcher.config import config
from aspinwall.launcher.widgets import LauncherWidget
import aspinwall.launcher.widget_chooser
from aspinwall.widgets.loader import get_widget_class_by_id

@Gtk.Template(resource_path='/org/dithernet/aspinwall/launcher/ui/widgetbox.ui')
class WidgetBox(Gtk.Box):
	"""Box that contains the widgets."""
	__gtype_name__ = 'WidgetBox'

	_widgets = []
	_drag_targets = []
	_removed_widgets = {}
	management_mode = False
	edit_mode = False

	widget_container = Gtk.Template.Child('widget-container')
	widget_chooser = Gtk.Template.Child('widget-chooser-container')
	toast_overlay = Gtk.Template.Child()

	chooser_button_revealer = Gtk.Template.Child()
	management_buttons_revealer = Gtk.Template.Child()

	def __init__(self):
		"""Initializes the widget box."""
		super().__init__()

		self._show_chooser_action = Gio.SimpleAction.new("show_widget_chooser", None)
		self._show_chooser_action.connect("activate", self.show_chooser)

		# WORKAROUND: For some reason, the revealer type in the widget chooser
		# resets itself to slide_down during this step. Force-set the type here
		# to avoid this.
		self.widget_chooser.set_transition_type(Gtk.RevealerTransitionType.SLIDE_LEFT)

		self._management_mode_action = Gio.SimpleAction.new("enter_widget_management", None)
		self._management_mode_action.connect("activate", self.enter_management_mode)

		# Set up the undo action
		self.install_action('toast.undo_remove', 's', self.undo_remove)

		# Set up autorefresh
		self.autorefresh_delay = config['autorefresh-delay']
		config.connect('changed::autorefresh-delay', self.set_autorefresh_delay)

		self.autorefresh_thread = threading.Thread(target=self.autorefresh, daemon=True)
		self.autorefresh_thread.start()

		# Let the widget chooser know a widgetbox has been created
		aspinwall.launcher.widget_chooser.widgetbox = self

		self.load_widgets()

	def set_autorefresh_delay(self, *args):
		"""Sets autorefresh delay from config."""
		self.autorefresh_delay = config['autorefresh-delay']

	def autorefresh(self):
		"""Automatically refreshes widgets at a given interval."""
		initial_delay = self.autorefresh_delay
		self.autorefresh_timer = self.autorefresh_delay
		while True:
			# If autorefresh is disabled, don't do anything
			if self.autorefresh_delay == 0:
				while self.autorefresh_delay != 0:
					time.sleep(1)

			self.autorefresh_timer -= 1
			if self.autorefresh_timer <= 0:
				for widget in self._widgets:
					widget._widget.refresh()
				self.autorefresh_timer = self.autorefresh_delay
			else:
				# Reset count if the delay is changed
				if initial_delay != self.autorefresh_delay:
					initial_delay = self.autorefresh_delay
					self.autorefresh_timer = self.autorefresh_delay
			time.sleep(1)

	def add_launcherwidget(self, launcherwidget):
		"""Adds a LauncherWidget to the WidgetBox."""
		self._widgets.append(launcherwidget)
		self.widget_container.append(launcherwidget)
		if self.management_mode:
			launcherwidget.widget_header_revealer.set_reveal_child(True)

	def add_widget(self, widget_class, instance=None):
		"""Adds a widget to the WidgetBox."""
		if not instance:
			instance = str(uuid.uuid4())
		aspwidget = LauncherWidget(widget_class, self, instance)
		self.add_launcherwidget(aspwidget)

		# We can only do this once the widget has been appended to the widgets list
		self.update_move_buttons()

		self.save_widgets()

	def undo_remove(self, a, b, instance):
		"""Un-does a widget remove."""
		_instance = instance.get_string()
		if _instance not in self._removed_widgets.keys():
			return False

		self.add_launcherwidget(self._removed_widgets[_instance])

	def drop_from_remove_buffer(self, dummy, instance):
		"""Removes a widget from the widget removal undo buffer."""
		if instance not in self._removed_widgets.keys():
			return False

		self._removed_widgets.pop(instance)

	def remove_widget(self, aspwidget):
		"""Removes a widget from the WidgetBox."""
		if self.management_mode:
			aspwidget.widget_header_revealer.set_reveal_child(False)
		else:
			aspwidget.widget_header.hide()
		self._widgets.remove(aspwidget)
		self.widget_container.remove(aspwidget)
		self.update_move_buttons()

		self.save_widgets()

		self._removed_widgets[aspwidget._widget.instance] = aspwidget

		# TRANSLATORS: Used in the popup that appears when you remove a widget
		toast = Adw.Toast.new(_("Removed “%s”") % aspwidget._widget.name) # noqa: F821
		toast.set_priority(Adw.ToastPriority.HIGH)
		# TRANSLATORS: Used in the popup that appears when you remove a widget
		toast.set_button_label(_('Undo')) # noqa: F821
		toast.set_detailed_action_name('toast.undo_remove')
		toast.set_action_target_value(GLib.Variant('s', aspwidget._widget.instance))
		toast.connect('dismissed', self.drop_from_remove_buffer, aspwidget._widget.instance)
		self.toast_overlay.add_toast(toast)

	def update_move_buttons(self):
		"""Updates the move buttons in all child LauncherWidget headers"""
		for widget in self._widgets:
			widget.widget_header.update_move_buttons()

	def get_widget_position(self, aspwidget):
		"""
		Returns the position of the LauncherWidget in the list (starting at 0),
		or None if the widget wasn't found.
		"""
		try:
			return self._widgets.index(aspwidget)
		except ValueError:
			return None

	def get_widget_at_position(self, pos):
		"""
		Returns the widget at the given position.
		"""
		return self._widgets[pos]

	def move_widget(self, old_pos, new_pos):
		"""
		Moves a widget from the provided position to the target position.
		"""
		if old_pos == new_pos:
			return True

		widget = self.get_widget_at_position(old_pos)

		if new_pos == 0:
			self.widget_container.reorder_child_after(widget)
			self._widgets.insert(0, self._widgets.pop(old_pos))
		else:
			if new_pos > old_pos:
				self.widget_container.reorder_child_after(widget, self.get_widget_at_position(new_pos))
				self._widgets.insert(new_pos, self._widgets.pop(old_pos))
			else:
				self.widget_container.reorder_child_after(widget, self.get_widget_at_position(new_pos - 1))
				self._widgets.insert(new_pos, self._widgets.pop(old_pos))

		self.update_move_buttons()
		self.save_widgets()

	def move_up(self, widget):
		"""Moves a LauncherWidget up in the box."""
		old_pos = self.get_widget_position(widget)
		if old_pos == 0:
			return None
		self.move_widget(old_pos, old_pos - 1)

	def move_down(self, widget):
		"""Moves a LauncherWidget down in the box."""
		old_pos = self.get_widget_position(widget)
		if old_pos == len(self._widgets) - 1:
			return None
		self.move_widget(old_pos, old_pos + 1)

	def save_widgets(self):
		"""Saves widgets to the config."""
		widget_list = []
		for widget in self._widgets:
			widget_list.append((widget._widget.metadata['id'], widget._widget.instance))
		config['widgets'] = widget_list

	def load_widgets(self):
		"""Loads widgets from the config."""
		widgets = config['widgets']
		if widgets:
			for widget in widgets:
				self.add_widget(get_widget_class_by_id(widget[0]), widget[1])

	@Gtk.Template.Callback()
	def show_chooser(self, *args):
		"""Shows the widget chooser."""
		self.widget_chooser.set_transition_type(Gtk.RevealerTransitionType.SLIDE_LEFT)
		self.widget_chooser.search.grab_focus()
		self.widget_chooser.set_reveal_child(True)

	def enter_management_mode(self, *args):
		"""Enters widget management mode."""
		self.management_mode = True
		self.edit_mode = True
		window = self.get_native()
		window.wallpaper.dim()
		window.clockbox.dim()

		window.app_chooser_button_revealer.set_reveal_child(False)
		window.app_chooser_show.set_sensitive(False)
		window.pause_focus_manager = True
		self.chooser_button_revealer.set_reveal_child(False)
		self.management_buttons_revealer.set_reveal_child(True)

		for widget in self._widgets:
			widget.reveal_header()
			widget.widget_content.set_sensitive(False)
			widget.edit_button_revealer.set_visible(False)
			widget.edit_button_revealer.set_sensitive(False)

	@Gtk.Template.Callback()
	def exit_management_mode(self, *args):
		"""Exits widget management mode."""
		if self.edit_mode:
			window = self.get_native()
			window.wallpaper.undim()
			window.clockbox.undim()

			if self.management_mode:
				for widget in self._widgets:
					if widget._widget.has_settings_menu:
						widget.hide_widget_settings()
					widget.widget_header_revealer.set_reveal_child(False)
					widget.widget_content.set_sensitive(True)
					widget.edit_button_revealer.set_visible(True)
					widget.edit_button_revealer.set_sensitive(True)
				window.app_chooser_show.set_sensitive(True)
				window.pause_focus_manager = False
				self.management_buttons_revealer.set_reveal_child(False)
				self.chooser_button_revealer.set_reveal_child(True)
			else:
				for widget in self._widgets:
					if widget._widget.has_settings_menu:
						widget.hide_widget_settings()
					widget.widget_header_revealer.set_reveal_child(False)
					widget.container.remove_css_class('dim')
					widget.widget_content.set_sensitive(True)
					widget.edit_button_revealer.set_visible(True)
					widget.edit_button_revealer.set_sensitive(True)
				window.app_chooser_show.set_sensitive(True)
				window.pause_focus_manager = False
				self.chooser_button_revealer.set_sensitive(True)

			window.app_chooser_button_revealer.set_reveal_child(True)

			self.management_mode = False
			self.edit_mode = False

@Gtk.Template(resource_path='/org/dithernet/aspinwall/launcher/ui/clockbox.ui')
class ClockBox(Gtk.Box, Dimmable):
	"""Box that contains the launcher's clock."""
	__gtype_name__ = 'ClockBox'

	clockbox_time = Gtk.Template.Child()
	clockbox_date = Gtk.Template.Child()

	def __init__(self):
		"""Initializes the clock box."""
		super().__init__()
		self.update_size()
		config.connect('changed::clock-size', self.update_size)
		clock_daemon.connect('notify::time', self.update)

	def update_size(self, *args):
		"""Updates the size of the clock based on the clock-size config."""
		size = config['clock-size']
		if size == 0:
			self.add_css_class('small')
			self.remove_css_class('medium')
			self.remove_css_class('large')
		elif size == 1:
			self.add_css_class('medium')
			self.remove_css_class('small')
			self.remove_css_class('large')
		elif size == 2:
			self.add_css_class('large')
			self.remove_css_class('small')
			self.remove_css_class('medium')

	def update(self, *args):
		"""Updates the time and date on the clock."""
		self.clockbox_time.set_markup(
			'<span weight="bold">' + time.strftime(config['time-format']) + '</span>'
		)
		self.clockbox_date.set_markup(
			'<span>' + time.strftime(config['date-format']) + '</span>'
		)
