# coding: utf-8
"""Contains window creation code for the Aspinwall launcher"""
from gi.repository import Adw, Gtk, Gio
import os
import time
import threading

from ..config import config

# The ClockBox, WidgetBox and AppChooser classes are imported to avoid
# "invalid object type" errors.
from .clockbox import ClockBox # noqa: F401
from .widgetbox import WidgetBox # noqa: F401
from .app_chooser import AppChooser # noqa: F401
from .widget_chooser import WidgetChooser # noqa: F401
from .wallpaper import Wallpaper # noqa: F401
from .settings import LauncherSettings

@Gtk.Template(resource_path='/org/dithernet/aspinwall/launcher/ui/launcher.ui')
class Launcher(Gtk.ApplicationWindow):
    """Base class for launcher window."""
    __gtype_name__ = 'Launcher'

    launcher_wallpaper_overlay = Gtk.Template.Child()
    wallpaper = Gtk.Template.Child('launcher_wallpaper')

    launcher_stack = Gtk.Template.Child()
    launcher_content = Gtk.Template.Child()

    clockbox = Gtk.Template.Child()
    widgetbox = Gtk.Template.Child()
    app_chooser = Gtk.Template.Child()
    app_chooser_show = Gtk.Template.Child()
    app_chooser_button_revealer = Gtk.Template.Child()
    widget_chooser = Gtk.Template.Child()
    widget_chooser_flap = Gtk.Template.Child()

    focused = True
    pause_focus_manager = False

    def __init__(self, application, in_shell=False, version='development'):
        """Initializes the launcher window."""
        super().__init__(
            application=application,
            title='Launcher'
        )
        self.version = version

        self.app_chooser_show.connect('clicked', self.show_app_chooser)

        self._show_chooser_action = Gio.SimpleAction.new("show_widget_chooser", None)
        self._show_chooser_action.connect("activate", self.show_chooser)

        self.open_settings_action = Gio.SimpleAction.new("open_settings", None)
        self.open_settings_action.connect('activate', self.open_settings)

        self.about_aspinwall_action = Gio.SimpleAction.new("about_aspinwall", None)
        self.about_aspinwall_action.connect('activate', self.open_about)

        self.add_action(self._show_chooser_action)
        self.add_action(self.widgetbox._management_mode_action)
        self.add_action(self.open_settings_action)
        self.add_action(self.about_aspinwall_action)

        self.launcher_wallpaper_overlay.set_measure_overlay(self.launcher_stack, True)

        # Set up idle mode

        # The motion controller is added/removed as needed, to avoid lag
        self.motion_controller = Gtk.EventControllerMotion.new()
        self.motion_controller.connect('motion', self.on_focus)

        self.click_controller = Gtk.GestureClick.new()
        self.click_controller.connect('pressed', self.on_focus)
        self.click_controller.connect('released', self.on_focus)
        self.add_controller(self.click_controller)

        self.focus_manager_thread = threading.Thread(target=self.focus_manager_loop, daemon=True)
        self.focus_manager_thread.start()

        config.connect('changed::idle-mode-delay', self.update_unfocus_countdown)

        self.connect('realize', self.on_realize)

    def on_realize(self, *args):
        surface = self.get_surface()
        surface.connect('notify::width', self.set_widgetbox_width)

    def set_widgetbox_width(self, *args):
        """Sets the widgetbox's width to match 50% of the screen."""
        width_request = self.get_surface().get_width() / 2 - 40
        if width_request > 0:
            self.clockbox.set_size_request(width_request, 0)
            self.widgetbox.set_size_request(width_request, 0)
        else:
            self.clockbox.set_size_request(0, 0)
            self.widgetbox.set_size_request(0, 0)

    def show_app_chooser(self, *args):
        """Shows the app chooser."""
        self.pause_focus_manager = True
        # Reload apps, clear search
        self.app_chooser.search.set_text('')
        self.app_chooser.update_model()

        # Select first item in list
        self.app_chooser.selection_model.select_item(0, True)
        # Scroll to top
        vadjust = self.app_chooser.app_grid_container.get_vadjustment()
        vadjust.set_value(vadjust.get_lower())

        # Show chooser
        self.launcher_stack.set_visible_child_name('app-chooser')
        self.app_chooser.search.grab_focus()

    def show_chooser(self, *args):
        """Shows the widget chooser."""
        self.widget_chooser_flap.set_reveal_flap(True)

    def update_unfocus_countdown(self, *args):
        """
        Used to update the unfocus countdown value whenever the setting
        changes.
        """
        self.unfocus_countdown = config['idle-mode-delay'] + 1

    def focus_manager_loop(self):
        """Loop that manages focused/unfocused mode. Run as a thread."""
        self.unfocus_countdown = config['idle-mode-delay'] + 1
        while True:
            if self.focused and not self.pause_focus_manager:
                self.unfocus_countdown -= 1
                if self.unfocus_countdown <= 0:
                    self.on_unfocus()
            time.sleep(1)

    def on_unfocus(self, *args):
        """Performs actions on unfocus."""
        if self.focused:
            self.focused = False
            self.unfocus_countdown = config['idle-mode-delay'] + 1
            self.app_chooser_button_revealer.set_reveal_child(False)
            self.widgetbox.chooser_button_revealer.set_reveal_child(False)
            self.launcher_content.add_css_class('unfocused')
            self.add_controller(self.motion_controller)

    def on_focus(self, *args):
        """Performs actions on focus."""
        if not self.focused:
            self.remove_controller(self.motion_controller)
            self.focused = True
            self.unfocus_countdown = config['idle-mode-delay'] + 1
            self.app_chooser_button_revealer.set_reveal_child(True)
            self.widgetbox.chooser_button_revealer.set_reveal_child(True)
            self.launcher_content.remove_css_class('unfocused')
        else:
            self.unfocus_countdown = config['idle-mode-delay'] + 1

    def open_settings(self, *args):
        """Opens the launcher settings window."""
        settings_window = LauncherSettings()
        settings_window.set_transient_for(self)
        settings_window.present()

    def open_about(self, *args):
        """Opens the about window."""
        about_dialog = Adw.AboutWindow(
            modal=True, transient_for=self,
            version=self.version,
            application_name='Aspinwall Launcher',
            # TRANSLATORS: This can also be translated as "developers".
            developer_name=_('Aspinwall contributors'), # noqa: F821
            license_type=Gtk.License.MIT_X11,
            website='https://github.com/aspinwall-ui/aspinwall-launcher',
            issue_url='https://github.com/aspinwall-ui/aspinwall-launcher/issues'
        )

        # TRANSLATORS: Set this to your name (and optionally the e-mail address).
        if _('translator-credits') != 'translator-credits': # noqa: F821
            about_dialog.set_translator_credits(_('translator-credits')) # noqa: F821

        about_dialog.show()
