# coding: utf-8
"""
World clock widget for Aspinwall
"""
from aspinwall_launcher.widgets import Widget
from aspinwall_launcher.utils.clock import clock_daemon
import gi
gi.require_version('GWeather', '4.0')
from gi.repository import Adw, GLib, Gtk, GWeather
translatable = lambda message: message
import gettext

def get_timezone_offset(timezone, use_local=False):
    """
    Convenience function to get an int representing the timezone offset
    compared to the UTC or local timezone, depending on the value of the
    use_local parameter.
    """
    interval = timezone.find_interval(
        GLib.TimeType.UNIVERSAL,
        GLib.DateTime.new_now(timezone).to_unix()
    )
    offset = timezone.get_offset(interval)
    if use_local:
        utc_offset = offset
        local_offset = get_timezone_offset(GLib.TimeZone.new_local())
        offset = utc_offset - local_offset
    return offset

class WorldClock(Widget):
    metadata = {
        "name": translatable("World Clock"),
        "icon": 'alarm-symbolic',
        "description": translatable("Check the time in another timezone"),
        "id": "org.dithernet.aspinwall.widgets.WorldClock",
        "tags": translatable('clock,timezone'),
        "author": translatable("Aspinwall developers"),
        "url": "https://github.com/aspinwall-ui/aspinwall-launcher",
        "issue_tracker": "https://github.com/aspinwall-ui/aspinwall-launcher/issues",
        "version": "0.0.1"
    }

    has_config = True
    has_settings_menu = True
    has_stylesheet = True
    has_gresource = True

    def __init__(self, instance):
        super().__init__(instance)
        _ = self.l

        self.location = None
        if self.config['location']:
            # We get it this way to prevent PyGObject from turning it
            # into a Python object (it has to be a GVariant)
            location_variant = self.config.get_value('location').\
                                get_child_value(0).get_child_value(0)
            self.location = GWeather.Location.get_world().deserialize(
                location_variant
            )

        self.content = Gtk.Box(
            orientation=Gtk.Orientation.VERTICAL,
            halign=Gtk.Align.CENTER,
            valign=Gtk.Align.CENTER,
            spacing=6
        )
        self.content.add_css_class('container')

        self.clock_label = Gtk.Label(label='00:00')
        self.clock_label.add_css_class('clock')
        self.clock_label.add_css_class('numeric')
        self.content.append(self.clock_label)

        self.timezone_label = Gtk.Label(wrap=True, justify=Gtk.Justification.CENTER)
        self.timezone_label.add_css_class('dim-label')
        self.timezone_label.add_css_class('timezone-label')
        self.content.append(self.timezone_label)

        clock_daemon.connect('notify::time', self.update)
        self.update()

        self.set_child(self.content)

        Adw.ActionRow()
        from .settings import ClockSettings
        self.set_settings_child(ClockSettings(self))

    def update(self, *args):
        """Updates the clock data every second."""
        _ = self.l
        if not self.location:
            self.timezone_label.set_label(
                _('No location selected. Open the widget settings and choose a location.')
            )
            return
        time = GLib.DateTime.new_now(self.location.get_timezone())
        if self.config['twelvehour-time']:
            time_string = time.format('%I:%M %p')
        else:
            time_string = time.format('%H:%M')
        self.clock_label.set_label(time_string)

        timezone_offset_hour = int(
            get_timezone_offset(self.location.get_timezone(), use_local=True) / 3600
        )
        if timezone_offset_hour > 0:
            timezone_offset_text = gettext.ngettext(
                '{n} hour later', '{n} hours later',
                timezone_offset_hour
            ).format(n=timezone_offset_hour)
        elif timezone_offset_hour < 0:
            timezone_offset_text = gettext.ngettext(
                '{n} hour earlier', '{n} hours earlier',
                timezone_offset_hour * -1
            ).format(n=timezone_offset_hour * -1)
        else: # timezone_offset_hour == 0
            timezone_offset_text = _('Same as local time')

        self.timezone_label.set_label(f'{self.location.get_name()} • {timezone_offset_text}')

_widget_class = WorldClock
