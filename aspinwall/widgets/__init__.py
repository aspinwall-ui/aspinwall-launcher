# coding: utf-8
"""
Contains base class and helper functions for creating widgets.

Code for loading widgets can be found in the loader submodule.
"""
from gi.repository import Gtk, GObject

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
	config = {}

	def __init__(self, config=None):
		super().__init__()
		self.content = Gtk.Box(hexpand=True)
		if config:
			self.config = config

	def refresh(self):
		"""(Optional) Runs in the background at the widget refresh interval.
		For more information, see docs/widgets/creating-widgets.md."""
		return

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
