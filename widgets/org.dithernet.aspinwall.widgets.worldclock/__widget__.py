# coding: utf-8
"""
World clock widget for Aspinwall
"""
from aspinwall_launcher.widgets import Widget
from aspinwall_launcher.utils.clock import clock_daemon
import gi
gi.require_version('GWeather', '4.0')
from gi.repository import Adw, GLib, Gtk, GWeather, Gio
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
        "description": translatable("Clock with a custom timezone selector."),
        "id": "org.dithernet.aspinwall.widgets.WorldClock",
        "tags": translatable('clock,timezone'),
        "author": translatable("Aspinwall developers"),
        "url": "https://github.com/aspinwall-ui/aspinwall-launcher",
        "issue_tracker": "https://github.com/aspinwall-ui/aspinwall-launcher",
        "version": "0.0.1"
    }

    has_config = True
    has_settings_menu = True
    has_stylesheet = True

    def __init__(self, instance):
        super().__init__(instance)
        self.active_selection_box = None
        self._ignore_sb_active_change = False
        _ = self.l

        self.location = None
        if self.config['location']:
            # We get it this way to prevent PyGObject from turning it
            # into a Python object (it has to be a GVariant)
            location_variant = self.config.get_value('location').get_child_value(0).get_child_value(0)
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
        self.content.append(self.timezone_label)

        clock_daemon.connect('notify::time', self.update)
        self.update()

        self.set_child(self.content)

        self.create_settings()

    def update(self, *args):
        """Updates the clock data every second."""
        _ = self.l
        if not self.location:
            self.timezone_label.set_label(_('No location selected. Open the widget settings and choose a location.'))
            return
        time = GLib.DateTime.new_now(self.location.get_timezone())
        self.clock_label.set_label(
            f'{str(time.get_hour()).rjust(2, "0")}:{str(time.get_minute()).rjust(2, "0")}'
        )
        timezone_offset_hour = int(get_timezone_offset(self.location.get_timezone(), use_local=True) / 3600)
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

    def create_settings(self):
        _ = self.l
        self.populate_locations_store()

        content_clamp = Adw.Clamp(margin_top=6, maximum_size=400)
        self.settings_content = Gtk.Box(
            orientation=Gtk.Orientation.VERTICAL,
            hexpand=True,
            vexpand=True,
            spacing=6
        )
        content_clamp.set_child(self.settings_content)
        self.set_settings_child(content_clamp)

        self.settings_searchentry = Gtk.SearchEntry(search_delay=500, placeholder_text=_('Search for a city'), hexpand=True)
        self.settings_searchentry.connect('search-changed', self.settings_locationbox_update_search)
        self.settings_content.append(self.settings_searchentry)

        self.settings_filter = Gtk.CustomFilter.new(self.settings_locationbox_filterfunc, None)
        self.settings_filterlist = Gtk.FilterListModel.new(
            self.locations_store,
            self.settings_filter
        )

        locationlist_scroll = Gtk.ScrolledWindow(hscrollbar_policy=Gtk.PolicyType.NEVER, hexpand=True, vexpand=True)
        location_selector = Gtk.ListBox(selection_mode=Gtk.SelectionMode.NONE, hexpand=True, margin_bottom=6)
        location_selector.add_css_class('boxed-list')
        location_selector.bind_model(self.settings_filterlist, self.settings_locationbox_bind)
        locationlist_scroll.set_child(location_selector)
        self.settings_content.append(locationlist_scroll)

    def settings_locationbox_bind(self, item):
        """Binds the list items in the app list."""
        row = Adw.ActionRow(
            title=item.get_name(), # city name
            subtitle=f'{item.get_parent().get_name()} • {item.get_timezone_str()}' # country name + timezone
        )
        selection_box = Gtk.CheckButton()
        selection_box.add_css_class('selection-mode')
        row.add_suffix(selection_box)
        row.set_activatable_widget(selection_box)
        if self.location and item == self.location:
            selection_box.set_active(True)
            self.active_selection_box = selection_box
        selection_box.connect('toggled', self.settings_locationbox_update_selection, item)
        return row

    def settings_locationbox_update_selection(self, selection_box, item):
        if self._ignore_sb_active_change:
            return

        if selection_box.get_active() == False:
            self._ignore_sb_active_change = True
            selection_box.set_active(True)
            self._ignore_sb_active_change = False
            return

        if self.active_selection_box:
            self._ignore_sb_active_change = True
            self.active_selection_box.set_active(False)
            self._ignore_sb_active_change = False
        self.active_selection_box = selection_box

        self.location = item
        print(item.get_level())
        self.config['location'] = (item.serialize(),)

    def settings_locationbox_update_search(self, *args):
        self.settings_filter.changed(Gtk.FilterChange.DIFFERENT)

    def settings_locationbox_filterfunc(self, item, *args):
        search = self.settings_searchentry.get_text()
        if not search:
            return False
        search = search.lower()

        if search in item.get_name().lower():
            return True
        if item.get_parent().get_name() and search in item.get_parent().get_name().lower():
            return True
        return False

    def populate_locations_store(self):
        # Get world; this will allow us to iterate over all available locations
        world = GWeather.Location.get_world()

        # Create ListStore for city locations
        self.locations_store = Gio.ListStore(item_type=GWeather.Location)

        # This loop iterates over all existing locations to find cities and named timezones
        # only.
        valid_levels = (GWeather.LocationLevel.CITY, GWeather.LocationLevel.NAMED_TIMEZONE)
        prev_loc_buffer = [world]
        loc_buffer = []
        while prev_loc_buffer:
            for child in prev_loc_buffer:
                iter_prev = None
                iter_location = child.next_child(None)
                while iter_location:
                    loc_buffer.append(iter_location)
                    iter_prev = iter_location
                    iter_location = child.next_child(iter_prev)
                if child.get_level() in valid_levels:
                    self.locations_store.append(child)
            prev_loc_buffer = loc_buffer
            loc_buffer = []

    def save(self, *args):
        """Saves the contents of the notepad."""
        textbuffer = self.textview.get_buffer()
        self.config['buffer'] = textbuffer.get_text(
            textbuffer.get_start_iter(),
            textbuffer.get_end_iter(),
            False
        )

_widget_class = WorldClock
