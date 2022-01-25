# coding: utf-8
"""
Contains code for the widget chooser and widget infoboxes for the chooser.
"""
from gi.repository import Gtk
import os

from aspinwall.widgets.loader import available_widgets

# Pointer to the widget box; set up by the WidgetBox __init__ function,
# required by the widget chooser as the widget addition target
# This is defined in this file and set externally to avoid circular imports.
widgetbox = None

@Gtk.Template(filename=os.path.join(os.path.dirname(__file__), 'ui', 'widgetinfobox.ui'))
class WidgetInfobox(Gtk.Box):
	"""
	Infobox for widgets displayed in the widget chooser dialog.
	"""
	__gtype_name__ = 'WidgetInfobox'

	widget_icon = Gtk.Template.Child('widget_infobox_icon')
	widget_name = Gtk.Template.Child('widget_infobox_name')
	widget_description = Gtk.Template.Child('widget_infobox_description')

	def __init__(self, widget):
		"""Initializes a widget infobox."""
		super().__init__()

		self.widget = widget

		self.widget_icon.set_from_icon_name(widget.metadata['icon'])
		self.widget_name.set_markup(
			'<span size="large" font="bold">' + widget.metadata['name'] + '</span>'
		)
		self.widget_description.set_markup(
			'<span size="medium">' + widget.metadata['description'] + '</span>'
		)

	@Gtk.Template.Callback()
	def add_widget_from_infobox(self, *args):
		"""Adds the widget to the widget box."""
		widgetbox.add_widget(self.widget)

@Gtk.Template(filename=os.path.join(os.path.dirname(__file__), 'ui', 'widgetchooser.ui'))
class WidgetChooser(Gtk.Revealer):
	"""
	Widget chooser dialog.
	"""
	__gtype_name__ = 'WidgetChooser'

	_content = Gtk.Template.Child('widget_chooser_content')

	def __init__(self):
		"""Initializes a widget chooser."""
		super().__init__()
		self.fill()

	def fill(self):
		"""Fills the widget chooser."""
		for widget in available_widgets:
			self._content.append(WidgetInfobox(widget))

	@Gtk.Template.Callback()
	def hide(self, *args):
		"""Hides the widget chooser."""
		self.set_reveal_child(False)
