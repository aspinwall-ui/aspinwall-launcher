# coding: utf-8
"""
Contains base class and helper functions for creating widgets.

Code for loading widgets can be found in the loader submodule.
"""
from gi.repository import Gtk, Gio, GObject
import os
import gettext

class Widget(GObject.GObject):
	"""
	Base class for Aspinwall widgets.

	In general, widgets need to define the following variables:
	  - metadata - dict containing widget metadata:
	               - name
				   - description
				   - tags (comma-separated string)
				   - thumbnail (url to image)
	  			   - icon - contains GTK icon name string
	  - refresh() - (function) runs in the background at the widget
	                refresh interval
	  - content - Widget content. This can be any GTK widget; by default,
	              an empty GtkBox is created.

	For more information, see docs/widgets/creating-widgets.md.
	"""
	__gtype_name__ = 'AspWidget'

	metadata = {}
	has_config = False
	has_settings_menu = False
	hide_edit_button = False
	schema_base_path = None # set up automatically if not set

	widget_path = None
	instance = None

	def __init__(self, instance=0):
		super().__init__()
		self.content = Gtk.Box(hexpand=True, orientation=Gtk.Orientation.VERTICAL)
		self.instance = instance

		# Set up i18n
		localedir = self.join_with_data_path('po')
		self.l = lambda message: message # noqa: E741
		if os.path.exists(localedir):
			gettext.bindtextdomain(self.id.lower(), localedir)
			self.l = lambda message: gettext.dgettext(self.id.lower(), message) # noqa: E741
			self.metadata['name'] = self.l(self.metadata['name'])
			self.metadata['description'] = self.l(self.metadata['description'])
			self.metadata['tags'] = self.l(self.metadata['tags'])

		# Set up style context, CSS provider
		style_context = self.content.get_style_context()
		self.css_provider = Gtk.CssProvider()
		style_context.add_provider(self.css_provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)

		# Set up config
		if self.has_config:
			self.schema_source = Gio.SettingsSchemaSource.new_from_directory(
				self.join_with_data_path('schemas'),
				Gio.SettingsSchemaSource.get_default(),
				False
			)
			schema = self.schema_source.lookup(self.metadata['id'], False)
			if not schema:
				raise Exception(
					"Plugin error: schema not found in schema source. Make sure that your schema ID matches the widget ID (note that both are case-sensitive)." # noqa: E501
				)

			if not self.schema_base_path:
				self.schema_base_path = '/' + self.metadata['id'].lower().replace('.', '/') + '/'

			self.config = Gio.Settings.new_full(schema, None, self.schema_base_path + str(instance) + '/')

	def join_with_data_path(self, *args):
		"""Joins path relative to widget data directory."""
		return os.path.join(os.path.dirname(self.widget_path), *args)

	def refresh(self):
		"""(Optional) Runs in the background at the widget refresh interval.
		For more information, see docs/widgets/creating-widgets.md."""
		return None

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
		return self.metadata['tags'].split(',')
