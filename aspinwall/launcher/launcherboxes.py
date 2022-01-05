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
import aspinwall.launcher.widgetchooser
from aspinwall.widgets.loader import get_widget_class_by_id, load_widgets

@Gtk.Template(filename=os.path.join(os.path.dirname(__file__), 'ui', 'widgetbox.ui'))
class WidgetBox(Gtk.Box):
	"""Box that contains the widgets."""
	__gtype_name__ = 'WidgetBox'

	_widgets = []

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
		aspinwall.launcher.widgetchooser.widgetbox = self

		self.load_widgets()

	def add(self, widget_class, config={}):
		"""Adds a widget to the WidgetBox."""
		aspwidget = AspWidget(widget_class, config)
		self._widgets.append(aspwidget)
		self.widget_container.append(aspwidget)
		self.save_widgets()

	def remove(self, aspwidget):
		"""Removes a widget from the WidgetBox."""
		self._widgets.remove(aspwidget)
		self.widget_container.remove(aspwidget)
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
