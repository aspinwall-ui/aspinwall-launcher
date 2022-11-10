# coding: utf-8
"""
Contains code for the WidgetBox.
"""
from gi.repository import Adw, GLib, Gtk, Gio
import threading
import time

from ..config import config
from .widgetmanager import widget_manager
from .widgetview import WidgetView

@Gtk.Template(resource_path='/org/dithernet/aspinwall/launcher/ui/widgetbox.ui')
class WidgetBox(Gtk.Box):
    """Box that contains the widgets."""
    __gtype_name__ = 'WidgetBox'

    _drag_targets = []
    _removed_widgets = {}
    management_mode = False
    edit_mode = False

    widget_container = Gtk.Template.Child()
    toast_overlay = Gtk.Template.Child()

    chooser_button_revealer = Gtk.Template.Child()
    management_buttons_revealer = Gtk.Template.Child()

    def __init__(self):
        """Initializes the widget box."""
        super().__init__()

        self._management_mode_action = Gio.SimpleAction.new("enter_widget_management", None)
        self._management_mode_action.connect("activate", self.enter_management_mode)

        # Set up the undo action
        self.install_action('toast.undo_remove', 's', self.undo_remove)

        # Set up autorefresh
        self.auto_refresh_frequency = config['widget-autorefresh-frequency']
        config.connect('changed::autorefresh-delay', self.set_auto_refresh_frequency)

        self.autorefresh_thread = threading.Thread(target=self.autorefresh, daemon=True)
        self.autorefresh_thread.start()

        self.widget_container.bind_model(widget_manager.widgets, self.bind)
        widget_manager.widgets.connect('items-changed', self.update_move_buttons)

        self.update_move_buttons()

    def iterate_over_all_widgetviews(self, iter_func):
        """
        Runs a function against all widgetviews. Provides the widgetview
        in the widgetview kwarg.
        """
        for item_count in range(0, widget_manager.widgets.get_n_items()):
            widgetview = self.widget_container.get_row_at_index(item_count).get_child()
            iter_func(widgetview=widgetview)

    def bind(self, widget, *args):
        """Binds the list items in the widget list."""
        widgetview = WidgetView(self)
        widgetview.bind_to_widget(widget)
        return widgetview

    # Code for handling widget removal undo
    def undo_remove(self, a, b, instance):
        """Un-does a widget remove."""
        _instance = instance.get_string()
        if _instance not in self._removed_widgets.keys():
            return False

        widget_manager.add_widget(self._removed_widgets[_instance])
        self._removed_widgets.pop(_instance)

    def drop_from_remove_buffer(self, dummy, instance):
        """Removes a widget from the widget removal undo buffer."""
        if instance not in self._removed_widgets.keys():
            return False

        self._removed_widgets.pop(instance)

    def remove_widget(self, widgetview):
        """Removes a widget from the WidgetBox."""
        if self.management_mode:
            widgetview.widget_header_revealer.set_reveal_child(False)
        else:
            widgetview.widget_header.hide()
        widget_manager.remove_widget(widgetview._widget)

        self._removed_widgets[widgetview._widget.instance] = widgetview._widget

        # TRANSLATORS: Used in the popup that appears when you remove a widget
        toast = Adw.Toast.new(_("Removed “%s”") % widgetview._widget.name) # noqa: F821
        toast.set_priority(Adw.ToastPriority.HIGH)
        # TRANSLATORS: Used in the popup that appears when you remove a widget
        toast.set_button_label(_('Undo')) # noqa: F821
        toast.set_detailed_action_name('toast.undo_remove')
        toast.set_action_target_value(GLib.Variant('s', widgetview._widget.instance))
        toast.connect('dismissed', self.drop_from_remove_buffer, widgetview._widget.instance)
        self.toast_overlay.add_toast(toast)

    def update_move_buttons(self, *args):
        """Updates the move buttons in all child WidgetView headers"""
        self.iterate_over_all_widgetviews(
            lambda widgetview: widgetview.widget_header.update_move_buttons()
        )

    @Gtk.Template.Callback()
    def show_widget_chooser(self, *args):
        self.get_native().widget_chooser.show()

    def move_widget(self, old_pos, new_pos):
        """
        Moves a widget from the provided position to the target position.
        """
        widget_manager.move_widget(old_pos, new_pos)

        # Since we just re-created the WidgetViews, they're currently unaware of the
        # fact that we're still in editing mode; bump them to reflect that
        new_pos_widgetview = self.widget_container.get_row_at_index(new_pos).get_child()
        new_pos_widgetview.widget_header_revealer.set_visible(False) # skip animation
        new_pos_widgetview.reveal_header()
        new_pos_widgetview.widget_header_revealer.set_visible(True)

        self.update_move_buttons()

    def move_up(self, widget):
        """Moves a WidgetView up in the box."""
        old_pos = widget_manager.get_widget_position(widget._widget)
        if old_pos == 0:
            return None
        self.move_widget(old_pos, old_pos - 1)

    def move_down(self, widget):
        """Moves a WidgetView down in the box."""
        old_pos = widget_manager.get_widget_position(widget._widget)
        if old_pos == widget_manager.widgets.get_n_items() - 1:
            return None
        self.move_widget(old_pos, old_pos + 1)

    def set_auto_refresh_frequency(self, *args):
        """Sets autorefresh delay from config."""
        self.auto_refresh_frequency = config['widget-autorefresh-frequency']

    def autorefresh(self):
        """Automatically refreshes widgets at a given interval."""
        initial_delay = self.auto_refresh_frequency
        self.auto_refresh_timer = self.auto_refresh_frequency
        while True:
            # If autorefresh is disabled, don't do anything
            if self.auto_refresh_frequency == 0:
                while self.auto_refresh_frequency != 0:
                    time.sleep(1)

            self.auto_refresh_timer -= 1
            if self.auto_refresh_timer < 0:
                for widget in widget_manager.widgets:
                    widget.refresh()
                self.auto_refresh_timer = self.auto_refresh_frequency
            else:
                # Reset count if the delay is changed
                if initial_delay != self.auto_refresh_frequency:
                    initial_delay = self.auto_refresh_frequency
                    self.auto_refresh_timer = self.auto_refresh_frequency
            time.sleep(1)

    def enter_management_mode(self, *args):
        """Enters widget management mode."""
        self.management_mode = True
        self.edit_mode = True
        window = self.get_native()
        window.wallpaper.dim()
        window.clockbox.dim()

        window.app_chooser_button_revealer.set_reveal_child(False)
        window.app_chooser_show.set_sensitive(False)
        window.pause_focus_manager = True
        self.chooser_button_revealer.set_reveal_child(False)
        self.management_buttons_revealer.set_reveal_child(True)

        self.iterate_over_all_widgetviews(
            self.widget_callback_enter_management_mode
        )

    @Gtk.Template.Callback()
    def exit_management_mode(self, *args):
        """Exits widget management mode."""
        if self.edit_mode:
            window = self.get_native()
            if window.widget_chooser_flap.get_reveal_flap():
                window.widget_chooser.hide()
            window.wallpaper.undim()
            window.clockbox.undim()

            self.iterate_over_all_widgetviews(
                self.widget_callback_exit_management_mode
            )

            self.management_mode = False
            self.edit_mode = False

    def widget_callback_enter_management_mode(self, widgetview):
        """Functions to execute on every widgetview when entering management mode,"""
        widgetview.reveal_header()
        widgetview.widget_content.set_sensitive(False)
        widgetview.edit_button_revealer.set_visible(False)
        widgetview.edit_button_revealer.set_sensitive(False)

    def widget_callback_exit_management_mode(self, widgetview):
        """Functions to execute on every widgetview when exiting management mode,"""
        window = self.get_native()
        if widgetview._widget.has_settings_menu:
            widgetview.hide_widget_settings()

        widgetview.widget_header_revealer.set_reveal_child(False)
        widgetview.container.remove_css_class('dim')
        widgetview.widget_content.set_sensitive(True)

        widgetview.edit_button_revealer.set_visible(True)
        widgetview.edit_button_revealer.set_sensitive(True)
        window.app_chooser_button_revealer.set_reveal_child(True)
        window.app_chooser_show.set_sensitive(True)
        self.chooser_button_revealer.set_reveal_child(True)
        self.chooser_button_revealer.set_sensitive(True)
        self.management_buttons_revealer.set_reveal_child(False)

        window.pause_focus_manager = False
