# coding: utf-8
"""
Contains code for the ClockBox and WidgetBox.
"""
from gi.repository import Gtk
import os
import threading
import time

from aspinwall.launcher.config import config
from aspinwall.launcher.widgets import AspWidget
from aspinwall.widgets.loader import get_widget_class_by_id, load_widgets

@Gtk.Template(filename=os.path.join(os.path.dirname(__file__), 'ui', 'widgetbox.ui'))
class WidgetBox(Gtk.Box):
	"""Box that contains the widgets."""
	__gtype_name__ = 'WidgetBox'

	_widgets = []

	widget_container = Gtk.Template.Child('widget-container')

	def __init__(self):
		"""Initializes the widget box."""
		super().__init__()
		self.load_widgets()

	def add(self, widget_class, config={}, position=-1):
		"""Adds a widget to the WidgetBox."""
		aspwidget = AspWidget(widget_class, config)
		self._widgets.insert(position, aspwidget)
		if position == -1:
			self.widget_container.append(aspwidget)
		else:
			self.widget_container.insert_child_after(aspwidget, self._widgets[position])

		self.save_widgets()

	def load_widgets(self):
		"""Loads widgets from the config."""
		config.reload()
		widgets = config.get('widgets')
		if widgets:
			for widget in widgets:
				self.add(get_widget_class_by_id(widget['id']), widget['config'])

	def save_widgets(self):
		"""Saves the current widget configuration to the config."""
		widget_list = []
		for widget in self._widgets:
			widget_list.append({'id': widget._widget.metadata['id'], 'config': widget._widget.config})
		config.set('widgets', widget_list)
		config.save()

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
