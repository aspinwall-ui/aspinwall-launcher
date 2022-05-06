# coding: utf-8
"""
Contains basic code for the launcher's widget handling.
"""
from gi.repository import Gtk, Gdk, GObject

@Gtk.Template(resource_path='/org/dithernet/aspinwall/launcher/ui/widgetviewheader.ui')
class WidgetViewHeader(Gtk.Box):
	"""Header for a WidgetView."""
	__gtype_name__ = 'WidgetViewHeader'

	icon = Gtk.Template.Child('widget_header_icon')
	title = Gtk.Template.Child('widget_header_title')

	widget_settings_button = Gtk.Template.Child()
	move_up_button = Gtk.Template.Child('widget_header_move_up')
	move_down_button = Gtk.Template.Child('widget_header_move_down')

	def __init__(self, widget, widgetview):
		"""Initializes a WidgetViewHeader."""
		super().__init__()
		self._widget = widget
		self._widgetview = widgetview

		if self._widget.has_settings_menu:
			self.widget_settings_button.set_visible(True)
			self.widget_settings_button.set_sensitive(True)

		self.icon.set_from_icon_name(self._widget.metadata['icon'])
		self.title.set_label(self._widget.metadata['name'])

		self.add_controller(self._widgetview.drag_source)

	@Gtk.Template.Callback()
	def move_up(self, *args):
		"""Moves the parent WidgetView up."""
		self._widgetview._widgetbox.move_up(self._widgetview)
		self.update_move_buttons()

	@Gtk.Template.Callback()
	def move_down(self, *args):
		"""Moves the parent WidgetView down."""
		self._widgetview._widgetbox.move_down(self._widgetview)
		self.update_move_buttons()

	@Gtk.Template.Callback()
	def remove(self, *args):
		"""Removes the parent WidgetView."""
		self._widgetview.remove()

	@Gtk.Template.Callback()
	def hide(self, *args):
		"""Hides the widget header."""
		self._widgetview.edit_button_revealer.set_reveal_child(False)
		if not self._widgetview._widgetbox.management_mode:
			for widget in self._widgetview._widgetbox._widgets:
				widget.container.remove_css_class('dim')
				widget.edit_button_revealer.set_visible(True)
				widget.edit_button_revealer.set_sensitive(True)

			window = self.get_native()
			window.wallpaper.undim()
			window.clockbox.undim()
			self._widgetview.widget_content.set_sensitive(True)

			self.get_native().app_chooser_show.set_sensitive(True)
			self._widgetview._widgetbox.chooser_button_revealer.set_sensitive(True)
			self.get_parent().set_reveal_child(False)
			self._widgetview._widgetbox.edit_mode = False
		else:
			self._widgetview._widgetbox.exit_management_mode()

	@Gtk.Template.Callback()
	def show_widget_settings(self, *args):
		"""Shows the widget settings overlay."""
		self._widgetview.widget_settings_revealer.set_visible(True)
		self._widgetview.widget_settings_revealer.set_reveal_child(True)

	def update_move_buttons(self):
		"""
		Makes the move buttons sensitive or non-sensitive based on whether
		moving the widget up/down is possible.
		"""
		position = self._widgetview.get_position()

		if position == 0:
			self.move_up_button.set_sensitive(False)
		else:
			self.move_up_button.set_sensitive(True)

		if position == len(self._widgetview._widgetbox._widgets) - 1:
			self.move_down_button.set_sensitive(False)
		else:
			self.move_down_button.set_sensitive(True)

@Gtk.Template(resource_path='/org/dithernet/aspinwall/launcher/ui/widgetview.ui')
class WidgetView(Gtk.Box):
	"""
	Box containing a widget, alongside with its header.
	This class is used in the launcher to display widgets.

	For information on creating widgets, see docs/widgets/creating-widgets.md.
	"""
	__gtype_name__ = 'WidgetView'

	container = Gtk.Template.Child()
	container_overlay = Gtk.Template.Child()
	widget_header_revealer = Gtk.Template.Child()
	widget_settings_revealer = Gtk.Template.Child()
	widget_settings_container = Gtk.Template.Child()
	edit_button_revealer = Gtk.Template.Child()

	def __init__(self, widget_class, widgetbox, instance):
		"""Initializes a widget display."""
		super().__init__()

		try:
			self._widget = widget_class(instance)
		except TypeError:
			print("FAIL!!!")
			return
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

		self.widget_header = WidgetViewHeader(self._widget, self)
		self.widget_header_revealer.set_child(self.widget_header)

		self.widget_content = self._widget.content
		self.widget_content.add_css_class('aspinwall-widget-content')
		self.container.append(self.widget_content)

		if self._widget.has_settings_menu:
			self.widget_settings_container.append(self._widget.settings_menu)

		# Set up long-press target
		longpress = Gtk.GestureLongPress()
		longpress.connect('pressed', self.reveal_header)
		self.widget_content.add_controller(longpress)

		# Set up click target
		dismiss_click = Gtk.GestureClick()
		dismiss_click.connect('pressed', self._widgetbox.exit_management_mode)
		self.widget_content.add_controller(dismiss_click)

		# Set up hover target
		hover = Gtk.EventControllerMotion()
		hover.connect('enter', self.reveal_edit_button)
		hover.connect('leave', self.hide_edit_button)
		self.container_overlay.add_controller(hover)

	def remove(self):
		"""Removes the widget from its parent WidgetBox."""
		self._widgetbox.remove_widget(self)

	def get_position(self):
		"""Returns the WidgetView's position in its parent widgetbox."""
		return self._widgetbox.get_widget_position(self)

	@Gtk.Template.Callback()
	def reveal_header(self, *args):
		"""Reveals the widget's header."""
		self.edit_button_revealer.set_visible(False)
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
					widget.edit_button_revealer.set_visible(False)
					widget.edit_button_revealer.set_sensitive(False)
				else:
					widget.container.remove_css_class('dim')
			self.get_native().app_chooser_show.set_sensitive(False)
			self._widgetbox.chooser_button_revealer.set_sensitive(False)
			self._widgetbox.edit_mode = True
		self.widget_header_revealer.set_reveal_child(True)

	@Gtk.Template.Callback()
	def hide_widget_settings(self, *args):
		"""Hides the widget's settings menu."""
		self.widget_settings_revealer.set_reveal_child(False)
		self.widget_settings_revealer.set_visible(False)

	def reveal_edit_button(self, *args):
		"""Reveals the edit button."""
		self.edit_button_revealer.set_reveal_child(True)

	def hide_edit_button(self, *args):
		"""Hides the edit button."""
		self.edit_button_revealer.set_reveal_child(False)

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
