# coding: utf-8
"""
Contains basic code for the launcher's widget handling.
"""
from gi.repository import Gtk, Gdk, GObject
import os

@Gtk.Template(filename=os.path.join(os.path.dirname(__file__), 'ui', 'widgetheader.ui'))
class AspWidgetHeader(Gtk.Box):
	"""Header for AspWidget."""
	__gtype_name__ = 'AspWidgetHeader'

	icon = Gtk.Template.Child('widget_header_icon')
	title = Gtk.Template.Child('widget_header_title')

	move_up_button = Gtk.Template.Child('widget_header_move_up')
	move_down_button = Gtk.Template.Child('widget_header_move_down')

	def __init__(self, widget, aspwidget):
		"""Initializes an AspWidgetHeader."""
		super().__init__()
		self._widget = widget
		self._aspwidget = aspwidget

		self.icon.set_from_icon_name(self._widget.icon)
		self.title.set_label(self._widget.title)

		self.add_controller(self._aspwidget.drag_source)

	@Gtk.Template.Callback()
	def move_up(self, *args):
		"""Moves the parent AspWidget up."""
		self._aspwidget._widgetbox.move_up(self._aspwidget)
		self.update_move_buttons()

	@Gtk.Template.Callback()
	def move_down(self, *args):
		"""Moves the parent AspWidget down."""
		self._aspwidget._widgetbox.move_down(self._aspwidget)
		self.update_move_buttons()

	@Gtk.Template.Callback()
	def remove(self, *args):
		"""Removes the parent AspWidget."""
		self._aspwidget.remove()

	def update_move_buttons(self):
		"""
		Makes the move buttons sensitive or non-sensitive based on whether
		moving the widget up/down is possible.
		"""
		position = self._aspwidget.get_position()

		if position == 0:
			self.move_up_button.set_sensitive(False)
		else:
			self.move_up_button.set_sensitive(True)

		if position == len(self._aspwidget._widgetbox._widgets) - 1:
			self.move_down_button.set_sensitive(False)
		else:
			self.move_down_button.set_sensitive(True)

@Gtk.Template(filename=os.path.join(os.path.dirname(__file__), 'ui', 'aspwidget.ui'))
class AspWidget(Gtk.Box):
	"""
	Box containing a widget, alongside with its header.

	This class is used to display widgets, and uses the Widget class as
	the widget content.

	For information on creating widgets, see docs/widgets/creating-widgets.md.
	"""
	__gtype_name__ = 'AspWidget'

	container = Gtk.Template.Child()

	def __init__(self, widget_class, widgetbox, config={}):
		"""Initializes a widget display."""
		super().__init__()

		self._widget = widget_class(config)
		self._widgetbox = widgetbox

		# Set up drag source
		self.drag_source = Gtk.DragSource(actions=Gdk.DragAction.MOVE)
		self.drag_source.connect("prepare", self.drag_prepare)
		self.drag_source.connect("drag-begin", self.drag_begin)
		self.drag_source.connect("drag-end", self.drag_end)
		# End drag source setup

		# Set up drop target
		self.drop_target = Gtk.DropTarget(actions=Gdk.DragAction.MOVE)
		self.drop_target.set_gtypes([GObject.TYPE_INT])
		self.add_controller(self.drop_target)

		self.drop_target.connect('drop', self.on_drop)
		self.drop_target.connect('enter', self.on_enter)
		self.drop_target.connect('leave', self.on_leave)
		# End drop target setup

		self.widget_header = AspWidgetHeader(self._widget, self)
		self.container.append(self.widget_header)

		self.widget_content = self._widget
		self.widget_content.add_css_class('aspinwall-widget-content')
		self.container.append(self.widget_content)

	def remove(self):
		"""Removes the widget from its parent WidgetBox."""
		self._widgetbox.remove_widget(self)

	def get_position(self):
		"""Returns the AspWidget's position in its parent widgetbox."""
		return self._widgetbox.get_widget_position(self)

	def drag_prepare(self, *args):
		"""Returns the GdkContentProvider for the drag operation"""
		return Gdk.ContentProvider.new_for_value(
			self.get_position()
		)

	def drag_begin(self, drag_source, *args):
		"""Operations to perform when the drag operation starts."""
		drag_source.set_icon(Gtk.WidgetPaintable(widget=self), self.get_allocation().width / 2, 10)
		self.add_css_class('dragged')

	def drag_end(self, *args):
		"""Operations to perform when the drag operation ends."""
		self.remove_css_class('dragged')

	def on_drop(self, stub, dropped_widget_pos, x, y):
		"""
		Performs the widget move when a dragged widget dropped.

		Note that this is performed from the perspective of the drop target;
		thus, self in this context is the widget which the dragged widget was
		dropped onto.
		"""
		drop_target_pos = self._widgetbox.get_widget_position(self)
		self._widgetbox.move_widget(dropped_widget_pos, drop_target_pos)
		self.remove_css_class('on-enter')

	def on_enter(self, *args):
		self.add_css_class('on-enter')
		return 0

	def on_leave(self, *args):
		self.remove_css_class('on-enter')
		return 0
