# coding: utf-8
"""
Contains base class and helper functions for creating widgets.

Code for loading widgets can be found in the loader submodule.
"""
from gi.repository import Gtk, GObject
import os

class Widget(GObject.GObject):
	"""
	Base class for Aspinwall widgets.

	In general, widgets need to define the following variables:
	  - metadata - dict containing widget metadata:
	               - name
				   - description
				   - tags (list)
				   - thumbnail (url to image)
	  			   - icon - contains GTK icon name string
	  - title - contains widget title, as displayed in the header
		        (can be changed dynaimcally)
	  - refresh() - (function) runs in the background at the widget
	                refresh interval
	  - content - Widget content. This can be any GTK widget; by default,
	              an empty GtkBox is created.

	For more information, see docs/widgets/creating-widgets.md.
	"""
	__gtype_name__ = 'AspWidget'

	metadata = {}
	has_config = False

	widget_path = None
	instance = None

	def __init__(self, instance=0):
		super().__init__()
		self.content = Gtk.Box(hexpand=True, orientation=Gtk.Orientation.VERTICAL)
		self.instance = instance

		# Set up style context, CSS provider
		style_context = self.content.get_style_context()
		self.css_provider = Gtk.CssProvider()
		style_context.add_provider(self.css_provider, 0)

		# Set up config
		if self.has_config:
			self.schema_source = Gio.SettingsSchemaSource.new_from_directory(
				self.join_with_data_path('schemas')
			)
			schema = Gio.SettingsSchemaSource.lookup(self.schema_source, self.metadata['id'], False)
			self.config = Gio.Settings.new_full(schema, None, self.schema_path + '/' + instance)

	def join_with_data_path(self, *args):
		"""Joins path relative to widget data directory."""
		return os.path.join(os.path.dirname(self.widget_path), *args)

	def refresh(self):
		"""(Optional) Runs in the background at the widget refresh interval.
		For more information, see docs/widgets/creating-widgets.md."""
		return

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
