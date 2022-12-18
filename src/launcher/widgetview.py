# coding: utf-8
"""
Contains basic code for the launcher's widget handling.
"""
from gi.repository import Gtk, Gdk, GObject
import time

from .widgetmanager import widget_manager

@Gtk.Template(resource_path='/org/dithernet/aspinwall/launcher/ui/widgetviewheader.ui')
class WidgetViewHeader(Gtk.CenterBox):
    """Header for a WidgetView."""
    __gtype_name__ = 'WidgetViewHeader'

    title = Gtk.Template.Child('widget_header_title')

    widget_refresh_button = Gtk.Template.Child()
    widget_settings_button = Gtk.Template.Child()
    move_up_button = Gtk.Template.Child('widget_header_move_up')
    move_down_button = Gtk.Template.Child('widget_header_move_down')

    def __init__(self, widget, widgetview):
        """Initializes a WidgetViewHeader."""
        super().__init__()
        self._widget = widget
        self._widgetview = widgetview

        if not self._widget.has_settings_menu:
            self.widget_settings_button.set_sensitive(False)

        if not self._widget.has_refresh:
            self.widget_refresh_button.set_sensitive(False)

        self.title.set_label(self._widget.metadata['name'])

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

    def _hide_widgetview_callback(self, widgetview):
        """Used by hide on all widgetviews."""
        widgetview.container.remove_css_class('dim')
        widgetview.edit_button_revealer.set_visible(True)
        widgetview.edit_button_revealer.set_sensitive(True)

    @Gtk.Template.Callback()
    def hide(self, *args):
        """Hides the widget header."""
        self._widgetview.edit_button_revealer.set_reveal_child(False)
        if not self._widgetview._widgetbox.management_mode:
            self._widgetview._widgetbox.iterate_over_all_widgetviews(
                self._hide_widgetview_callback
            )

            window = self.get_native()
            if not window.widget_chooser_flap.get_reveal_flap():
                window.wallpaper.undim()
                window.clockbox.undim()
                self._widgetview._widgetbox.chooser_button_revealer.set_sensitive(True)
            self._widgetview.widget_content.set_sensitive(True)

            self.get_native().app_chooser_show.set_sensitive(True)
            self.get_parent().set_reveal_child(False)
            self._widgetview._widgetbox.edit_mode = False
        else:
            self._widgetview._widgetbox.exit_management_mode()

    @Gtk.Template.Callback()
    def refresh_widget(self, *args):
        """Refreshes the widget represented by the widgetview."""
        self._widget.refresh()

    @Gtk.Template.Callback()
    def show_widget_settings(self, *args):
        """Shows the widget settings overlay."""
        self._widgetview.widget_settings_container.set_visible(True)
        self._widget._settings_toggled = True
        self._widget.notify('settings-toggled')
        self._widgetview.container_stack.set_visible_child(self._widgetview.widget_settings_container)

    @Gtk.Template.Callback()
    def show_widget_about(self, *args):
        """Shows the widget's about window."""
        self._widgetview._widget.show_about_window(self.get_native())

    def update_move_buttons(self):
        """
        Makes the move buttons sensitive or non-sensitive based on whether
        moving the widget up/down is possible.
        """
        position = widget_manager.get_widget_position(self._widgetview._widget)

        if position == 0:
            self.move_up_button.set_sensitive(False)
        else:
            self.move_up_button.set_sensitive(True)

        if position == widget_manager.widgets.get_n_items() - 1:
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
    container_stack = Gtk.Template.Child()
    container_overlay = Gtk.Template.Child()
    widget_header_revealer = Gtk.Template.Child()
    widget_settings_container = Gtk.Template.Child()
    edit_button_revealer = Gtk.Template.Child()
    edit_button = Gtk.Template.Child()

    def __init__(self, widgetbox):
        """Initializes a widget display."""
        super().__init__()
        self._widget = None
        self._widgetbox = widgetbox

        # Needed to recognize gestures; we don't actually do anything with it here,
        # but it is used by clickout in the window
        self.clickin_gesture = Gtk.GestureClick()
        self.add_controller(self.clickin_gesture)

    def bind_to_widget(self, widget):
        """Binds the WidgetView to a widget."""
        self._widget = widget
        self.widget_header = WidgetViewHeader(self._widget, self)
        self.widget_header_revealer.set_child(self.widget_header)

        self.widget_content = self._widget._container
        self.widget_content.add_css_class('aspinwall-widget-content')
        self.widget_content.unparent()
        self.container.append(self.widget_content)

        if self._widget.has_settings_menu:
            self.widget_settings_container.append(self._widget._settings_container)
            self.widget_settings_container.set_visible(False)

        # Set up long-press target
        longpress = Gtk.GestureLongPress()
        longpress.connect('pressed', self.reveal_header)
        self.widget_content.add_controller(longpress)

        # Set up click target
        dismiss_click = Gtk.GestureClick()
        dismiss_click.connect('pressed', self._widgetbox.exit_management_mode)
        self.widget_content.add_controller(dismiss_click)

        if widget.hide_edit_button:
            self.edit_button.set_visible(False)
            self.edit_button.set_sensitive(False)
        else:
            # Set up hover target
            hover = Gtk.EventControllerMotion()
            hover.connect('enter', self.on_hover)
            hover.connect('leave', self.on_unhover)
            self.container_stack.add_controller(hover)

        if self._widgetbox.management_mode:
            self.widget_content.set_sensitive(False)
            self.reveal_header()

        self.container_stack.connect(
            'notify::transition-running',
            self.handle_container_stack_transition_status
        )

    def remove(self):
        """Removes the widget from its parent WidgetBox."""
        self.container.remove(self.widget_content)
        if self._widget.has_settings_menu:
            self.widget_settings_container.remove(self._widget._settings_container)
        self._widgetbox.remove_widget(self)

    # Header/buttons

    def _reveal_header_callback(self, widgetview):
        """Used by reveal_header on all widgetviews."""
        if widgetview._widget.instance != self._widget.instance:
            widgetview.widget_header_revealer.set_reveal_child(False)
            widgetview.container.add_css_class('dim')
            widgetview.edit_button_revealer.set_visible(False)
            widgetview.edit_button_revealer.set_sensitive(False)
        else:
            widgetview.container.remove_css_class('dim')

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
            self._widgetbox.iterate_over_all_widgetviews(
                self._reveal_header_callback
            )
            window.app_chooser_show.set_sensitive(False)
            self._widgetbox.chooser_button_revealer.set_sensitive(False)
            self._widgetbox.edit_mode = True
        self.widget_header_revealer.set_reveal_child(True)

    @Gtk.Template.Callback()
    def hide_widget_settings(self, *args):
        """Hides the widget's settings menu."""
        self._widget._settings_toggled = False
        self._widget.notify('settings-toggled')
        self.container_stack.set_visible_child(self.container_overlay)

    def handle_container_stack_transition_status(self, stack, *args):
        # Transition to widget
        if self.container_stack.get_visible_child() == self.container_overlay:
            if not stack.get_transition_running():
                self.widget_settings_container.set_visible(False)
        else: # Transition to settings
            self.widget_settings_container.set_visible(True)

    def on_hover(self, *args):
        self.edit_button_revealer.set_reveal_child(True)

    def on_unhover(self, *args):
        self.edit_button_revealer.set_reveal_child(False)
