# coding: utf-8
"""
Contains code for WidgetData, a wrapper for Widget objects that only stores
information needed for parsing widget information.
"""
from gi.repository import GObject

class WidgetData(GObject.Object):
	"""
	Wrapper for Widget classes that only stores information needed for
	parsing widget information.
	"""
	__gtype_name__ = 'WidgetData'

	def __init__(self, widget_class):
		"""Initializes a new WidgetData object."""
		super().__init__()
		self.widget_class = widget_class

		self.metadata = widget_class.metadata
		self.has_config = widget_class.has_config
		self.has_settings_menu = widget_class.has_settings_menu

	@GObject.Property
	def id(self):
		"""The ID of the widget, as defined in its metadata."""
		return self.metadata['id']

	@GObject.Property
	def name(self):
		"""The name of the widget, as defined in its metadata."""
		return self.metadata['name']

	@GObject.Property
	def icon_name(self):
		"""The icon name of the widget, as defined in its metadata."""
		return self.metadata['icon']

	@GObject.Property
	def description(self):
		"""The description of the widget, as defined in its metadata."""
		return self.metadata['description']

	@GObject.Property
	def tags(self):
		"""The tags of the widget, as defined in its metadata."""
		return self.metadata['tags']
