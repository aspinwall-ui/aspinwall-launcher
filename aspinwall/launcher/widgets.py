# coding: utf-8
"""
Contains basic code for the launcher's widget handling.
"""
from gi.repository import Gtk, Gdk
import os

@Gtk.Template(filename=os.path.join(os.path.dirname(__file__), 'ui', 'widgetheader.ui'))
class AspWidgetHeader(Gtk.Box):
	"""Header for AspWidget."""
	__gtype_name__ = 'AspWidgetHeader'

	icon = Gtk.Template.Child('widget_header_icon')
	title = Gtk.Template.Child('widget_header_title')

	def __init__(self, widget):
		"""Initializes an AspWidgetHeader."""
		super().__init__()
		self._widget = widget
		self.icon.set_from_icon_name(self._widget.icon)
		self.title.set_label(self._widget.title)

class AspWidget(Gtk.Box):
	"""
	Box containing a widget, alongside with its header.

	This class is used to display widgets, and uses the Widget class as
	the widget content.

	For information on creating widgets, see docs/widgets/creating-widgets.md.
	"""
	__gtype_name__ = 'AspWidget'

	def __init__(self, widget_class, config={}):
		"""Initializes a widget display."""
		super().__init__(orientation=Gtk.Orientation.VERTICAL, visible=True, valign=Gtk.Align.END, hexpand=True)
		self._widget = widget_class(config)

		self.widget_header = AspWidgetHeader(self._widget)
		self.append(self.widget_header)

		self.widget_content = self._widget
		self.widget_content.add_css_class('aspinwall-widget-content')
		self.append(self.widget_content)

		self.add_css_class('aspinwall-widget')
