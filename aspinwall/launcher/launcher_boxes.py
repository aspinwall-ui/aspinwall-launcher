# coding: utf-8
"""
Contains code for the ClockBox and WidgetBox.
"""
from gi.repository import Gtk, Gio
import os
import threading
import time

from aspinwall.launcher.config import config
from aspinwall.launcher.widgets import AspWidget
import aspinwall.launcher.widget_chooser
from aspinwall.widgets.loader import get_widget_class_by_id

@Gtk.Template(filename=os.path.join(os.path.dirname(__file__), 'ui', 'widgetbox.ui'))
class WidgetBox(Gtk.Box):
	"""Box that contains the widgets."""
	__gtype_name__ = 'WidgetBox'

	_widgets = []
	_drag_targets = []

	widget_container = Gtk.Template.Child('widget-container')
	widget_chooser = Gtk.Template.Child('widget-chooser-container')

	def __init__(self):
		"""Initializes the widget box."""
		super().__init__()

		self._show_chooser_action = Gio.SimpleAction.new("show_widget_chooser", None)
		self._show_chooser_action.connect("activate", self.show_chooser)

		# WORKAROUND: For some reason, the revealer type in the widget chooser
		# resets itself to slide_down during this step. Force-set the type here
		# to avoid this.
		self.widget_chooser.set_transition_type(Gtk.RevealerTransitionType.SLIDE_LEFT)

		# Let the widget chooser know a widgetbox has been created
		aspinwall.launcher.widget_chooser.widgetbox = self

		self.load_widgets()

	def add_widget(self, widget_class, config={}, no_save=False):
		"""Adds a widget to the WidgetBox."""
		aspwidget = AspWidget(widget_class, self, config)
		self._widgets.append(aspwidget)
		self.widget_container.append(aspwidget)

		# We can only do this once the widget has been appended to the widgets list
		self.update_move_buttons()

		if not no_save:
			self.save_widgets()

	def remove_widget(self, aspwidget):
		"""Removes a widget from the WidgetBox."""
		self._widgets.remove(aspwidget)
		self.widget_container.remove(aspwidget)
		self.update_move_buttons()
		self.save_widgets()

	def update_move_buttons(self):
		"""Updates the move buttons in all child AspWidget headers"""
		for widget in self._widgets:
			widget.widget_header.update_move_buttons()

	def get_widget_position(self, aspwidget):
		"""
		Returns the position of the AspWidget in the list (starting at 0),
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

	def move_up(self, widget):
		"""Moves an AspWidget up in the box."""
		old_pos = self.get_widget_position(widget)
		if old_pos == 0:
			return None
		self.move_widget(old_pos, old_pos - 1)

	def move_down(self, widget):
		"""Moves an AspWidget down in the box."""
		old_pos = self.get_widget_position(widget)
		if old_pos == len(self._widgets) - 1:
			return None
		self.move_widget(old_pos, old_pos + 1)

	def load_widgets(self):
		"""Loads widgets from the config."""
		config.reload()
		widgets = config.get('widgets')
		if widgets:
			for widget in widgets:
				self.add_widget(get_widget_class_by_id(widget['id']), widget['config'], no_save=True)

	def save_widgets(self):
		"""Saves the current widget configuration to the config."""
		widget_list = []
		for widget in self._widgets:
			widget_list.append({'id': widget._widget.metadata['id'], 'config': widget._widget.config})
		config.set('widgets', widget_list)
		config.save()

	def show_chooser(self, *args):
		"""Shows the widget chooser."""
		self.widget_chooser.set_transition_type(Gtk.RevealerTransitionType.SLIDE_LEFT)
		self.widget_chooser.set_reveal_child(True)

@Gtk.Template(filename=os.path.join(os.path.dirname(__file__), 'ui', 'clockbox.ui'))
class ClockBox(Gtk.Box):
	"""Box that contains the launcher's clock."""
	__gtype_name__ = 'ClockBox'

	clockbox_time = Gtk.Template.Child()
	clockbox_date = Gtk.Template.Child()

	def __init__(self):
		"""Initializes the clock box."""
		super().__init__()

		self._updater = threading.Thread(target=self.update, daemon=True)
		self._updater.start()

	def update(self):
		"""Updates the time and date on the clock."""
		while True:
			self.clockbox_time.set_markup('<span weight="bold" font="28">' + time.strftime("%X") + '</span>')
			self.clockbox_date.set_markup('<span font="22">' + time.strftime("%A, %x") + '</span>')
			time.sleep(1)