# coding: utf-8
"""
Contains base class and helper functions for creating widgets.

Code for loading widgets can be found in the loader submodule.
"""
from gi.repository import Gtk

class Widget(Gtk.Box):
	"""
	Base class for Aspinwall widgets.

	In general, widgets need to define the following variables:
	  - metadata - dict containing widget metadata:
	               - name
				   - description
				   - tags (list)
				   - image_urls (list)
	  - icon - contains GTK icon string
	  - title - contains widget title, as displayed in the header
		        (can be changed dynaimcally)
	  - refresh() - (function) runs in the background at the widget
	                refresh interval

	For more information, see docs/widgets/creating-widgets.md.
	"""
	__gtype_name__ = 'AspWidgetContent'

	metadata = {}
	config = {}

	def __init__(self, config=None):
		super().__init__(valign=Gtk.Align.START, can_focus=True, hexpand=True)
		if config:
			self.config = config

	def refresh(self):
		"""(Optional) Runs in the background at the widget refresh interval.
		For more information, see docs/widgets/creating-widgets.md."""
		return
