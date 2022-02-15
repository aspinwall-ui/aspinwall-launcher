# coding: utf-8
"""
Contains basic code for the launcher's widget handling.
"""
from gi.repository import Gtk, Gdk, GObject

@Gtk.Template(resource_path='/org/dithernet/aspinwall/launcher/ui/widgetheader.ui')
class LauncherWidgetHeader(Gtk.Box):
	"""Header for LauncherWidget."""
	__gtype_name__ = 'LauncherWidgetHeader'

	icon = Gtk.Template.Child('widget_header_icon')
	title = Gtk.Template.Child('widget_header_title')

	move_up_button = Gtk.Template.Child('widget_header_move_up')
	move_down_button = Gtk.Template.Child('widget_header_move_down')

	def __init__(self, widget, aspwidget):
		"""Initializes a LauncherWidgetHeader."""
		super().__init__()
		self._widget = widget
		self._aspwidget = aspwidget

		self.icon.set_from_icon_name(self._widget.metadata['icon'])
		self.title.set_label(self._widget.metadata['name'])

		self.add_controller(self._aspwidget.drag_source)

	@Gtk.Template.Callback()
	def move_up(self, *args):
		"""Moves the parent LauncherWidget up."""
		self._aspwidget._widgetbox.move_up(self._aspwidget)
		self.update_move_buttons()

	@Gtk.Template.Callback()
	def move_down(self, *args):
		"""Moves the parent LauncherWidget down."""
		self._aspwidget._widgetbox.move_down(self._aspwidget)
		self.update_move_buttons()

	@Gtk.Template.Callback()
	def remove(self, *args):
		"""Removes the parent AspWidget."""
		self._aspwidget.remove()

	@Gtk.Template.Callback()
	def hide(self, *args):
		"""Hides the widget header."""
		if not self._aspwidget._widgetbox.management_mode:
			for widget in self._aspwidget._widgetbox._widgets:
				widget.container.remove_css_class('dim')

			window = self.get_native()
			window.wallpaper.undim()
			window.clockbox.undim()
			self._aspwidget.widget_content.set_sensitive(True)

			self.get_native().app_chooser_show.set_sensitive(True)
			self._aspwidget._widgetbox.chooser_button_revealer.set_sensitive(True)
			self.get_parent().set_reveal_child(False)
			self._aspwidget._widgetbox.edit_mode = False
		else:
			self._aspwidget._widgetbox.exit_management_mode()

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

@Gtk.Template(resource_path='/org/dithernet/aspinwall/launcher/ui/launcherwidget.ui')
class LauncherWidget(Gtk.Box):
	"""
	Box containing a widget, alongside with its header.
	This class is used in the launcher to display widgets.

	For information on creating widgets, see docs/widgets/creating-widgets.md.
	"""
	__gtype_name__ = 'LauncherWidget'

	container = Gtk.Template.Child()
	widget_header_revealer = Gtk.Template.Child()

	def __init__(self, widget_class, widgetbox, instance):
		"""Initializes a widget display."""
		super().__init__()

		self._widget = widget_class(instance)
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

		self.widget_header = LauncherWidgetHeader(self._widget, self)
		self.widget_header_revealer.set_child(self.widget_header)

		self.widget_content = self._widget.content
		self.widget_content.add_css_class('aspinwall-widget-content')
		self.container.append(self.widget_content)

		# Set up long-press target
		longpress = Gtk.GestureLongPress()
		longpress.connect('pressed', self.reveal_header)
		self.widget_content.add_controller(longpress)

		# Set up click target
		dismiss_click = Gtk.GestureClick()
		dismiss_click.connect('pressed', self._widgetbox.exit_management_mode)
		self.widget_content.add_controller(dismiss_click)

		# TODO: Set up hover target

	def remove(self):
		"""Removes the widget from its parent WidgetBox."""
		self._widgetbox.remove_widget(self)

	def get_position(self):
		"""Returns the LauncherWidget's position in its parent widgetbox."""
		return self._widgetbox.get_widget_position(self)

	def reveal_header(self, *args):
		"""Reveals the widget's header."""
		if not self._widgetbox.management_mode:
			# Dim the window and all other widgets; in the case of widget
			# management mode, the window dimming part is done by the
			# WidgetBox.enter_management_mode() function
			window = self.get_native()
			window.wallpaper.dim()
			window.clockbox.dim()
			self.widget_content.set_sensitive(False)
			for widget in self._widgetbox._widgets:
				if widget._widget.instance != self._widget.instance:
					widget.widget_header_revealer.set_reveal_child(False)
					widget.container.add_css_class('dim')
				else:
					widget.container.remove_css_class('dim')
			self.get_native().app_chooser_show.set_sensitive(False)
			self._widgetbox.chooser_button_revealer.set_sensitive(False)
			self._widgetbox.edit_mode = True
		self.widget_header_revealer.set_reveal_child(True)

	def drag_prepare(self, *args):
		"""Returns the GdkContentProvider for the drag operation"""
		return Gdk.ContentProvider.new_for_value(
			self.get_position()
		)

	def drag_begin(self, drag_source, *args):
		"""Operations to perform when the drag operation starts."""
		drag_source.set_icon(
			Gtk.WidgetPaintable(widget=self.container),
			self.container.get_allocation().width / 2, 10
		)
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
