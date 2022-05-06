# coding: utf-8
"""
Contains code for the widget manager.
"""
from gi.repository import Gio
import uuid

from aspinwall.launcher.config import config
from aspinwall.widgets import Widget
from aspinwall.widgets.loader import (
	load_available_widgets,
	get_widget_class_by_id
)

class LoadedWidgetManager:
	"""
	Manages loading widgets from/saving widgets to the config and keeps a
	list of loaded widgets.
	"""
	__gtype_name__ = 'LoadedWidgetManager'

	def __init__(self):
		"""Initializes the WidgetManager."""
		self.widgets = Gio.ListStore(item_type=Widget)
		load_available_widgets()
		self.load_widgets()

	# Loading/saving
	def load_widgets(self):
		"""Loads widgets from the launcher config."""
		# Added widgets are internally stored in a (id, instance) format.
		for widget in config['widgets']:
			widget_id = widget[0]
			instance = widget[1]

			try:
				self.add_widget_by_id(widget_id, instance)
			except KeyError:
				print("Attempted to load " + widget_id + ", which does not exist!")
				print("Removing from config.")
				config['widgets'] = [x for x in config['widgets'] if x != widget]
				continue

	def save_widgets(self):
		"""Saves the loaded widgets into the launcher config."""
		loaded_widgets = []
		for widget in self.widgets:
			loaded_widgets.append([widget.id, widget.instance])
		config['widgets'] = loaded_widgets

	# Other operations
	def add_widget_by_class(self, widget_class):
		"""
		Takes the widget class, creates the widget object from it and adds
		the resulting widget to the loaded widget list.
		"""
		instance = str(uuid.uuid4())
		widget = widget_class(instance)
		self.add_widget(widget)

	def add_widget_by_id(self, widget_id, instance=None):
		"""
		Takes the ID (and optionally the instance) and adds the widget
		with the provided ID to the loaded widget list.
		"""
		if not instance:
			instance = str(uuid.uuid4())

		widget_class = get_widget_class_by_id(widget_id)
		if not widget_class:
			raise KeyError('Attempted to add ' + widget_id + ', which does not exist!')
		widget = widget_class(instance)

		self.add_widget(widget)

	def add_widget(self, widget):
		"""Adds a widget object directly to the loaded widget list."""
		self.widgets.append(widget)
		self.save_widgets()

	def remove_widget(self, widget):
		"""Removes a widget from the loaded widget list."""
		widget_position = self.widgets.find(widget)[1]
		self.widgets.remove(widget_position)
		self.save_widgets()

	def get_widget_position(self, widgetview):
		"""
		Returns the position of the widget in the loaded widget list
		(starting at 0), or None if the widget wasn't found.
		"""
		search = self.widgets.find(widgetview)
		if search[0] is False:
			return None
		return search[1]

	def get_widget_at_position(self, pos):
		"""
		Returns the widget at the given position.
		"""
		return self.widgets.get_item(pos)

	def move_widget(self, old_pos, new_pos):
		"""Moves a widget from the old position to the new position."""
		if old_pos == new_pos:
			return None

		old_pos_widget = self.get_widget_at_position(old_pos)
		new_pos_widget = self.get_widget_at_position(new_pos)

		old_pos_widget.content.unparent()
		new_pos_widget.content.unparent()

		self.widgets.splice(new_pos, 1, [old_pos_widget])
		self.widgets.splice(old_pos, 1, [new_pos_widget])

		self.save_widgets()

widget_manager = LoadedWidgetManager()
