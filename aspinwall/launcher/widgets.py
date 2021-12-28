# coding: utf-8
"""
Contains basic code for widgets.
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

	def __init__(self, widget):
		"""Initializes a widget display."""
		super().__init__(orientation=Gtk.Orientation.VERTICAL, visible=True, valign=Gtk.Align.END, hexpand=True)
		self._widget = widget

		self.widget_header = AspWidgetHeader(widget)
		self.append(self.widget_header)

		self.widget_content = self._widget
		self.widget_content.add_css_class('aspinwall-widget-content')
		self.append(self.widget_content)

		self.add_css_class('aspinwall-widget')

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

	def __init__(self):
		super().__init__(valign=Gtk.Align.START, can_focus=True, hexpand=True)

	def refresh(self):
		"""(Optional) Runs in the background at the widget refresh interval.
		For more information, see docs/widgets/creating-widgets.md."""
		return

class Welcome(Widget):
	title = "Welcome to Aspinwall"
	icon = 'dialog-information'
	metadata = {
		"name": "Welcome",
		"description": "Editable welcome widget; displays a simple tutorial and any distro-specific text",
	}

	def __init__(self):
		super().__init__()

		container = Gtk.Box()
		container.append(Gtk.Label(label='To add new widgets, press the '))
		container.append(Gtk.Image.new_from_icon_name('open-menu-symbolic'))
		container.append(Gtk.Label(label=' button in the top right corner.'))

		self.append(container)
