from gi.repository import Adw, Gtk, GWeather, Gio

@Gtk.Template(resource_path='/org/dithernet/aspinwall/widgets/WorldClock/ui/settings.ui')
class ClockSettings(Gtk.Box):
    __gtype_name__ = 'ClockSettings'

    settings_stack = Gtk.Template.Child()
    preferences = Gtk.Template.Child()
    location_selector = Gtk.Template.Child()

    location_list_box = Gtk.Template.Child()
    location_search_entry = Gtk.Template.Child()

    twelvehour_time_checkbutton = Gtk.Template.Child()

    def __init__(self, parent):
        Adw.Clamp() # bizzare fix for a bizzare bug...
        super().__init__()
        self._parent = parent
        self._initialized = False
        self.active_selection_box = None
        self._ignore_sb_active_change = False

        self.populate_locations_store()

        self.settings_filter = Gtk.CustomFilter.new(self.location_filterfunc, None)
        self.settings_filterlist = Gtk.FilterListModel.new(
            self.locations_store,
            self.settings_filter
        )
        self.location_list_box.bind_model(self.settings_filterlist, self.location_bind)

        self._parent.config.bind('twelvehour-time', self.twelvehour_time_checkbutton, 'active',
            Gio.SettingsBindFlags.DEFAULT
        )

        self._parent.connect('notify::settings-toggled', self.on_settings_toggle)

        self._initialized = True

    def on_settings_toggle(self, widget, *args):
        if widget._settings_toggled:
            self.close_location_selector()

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

    def location_bind(self, item):
        """Binds the list items in the app list."""
        row = Adw.ActionRow(
            title=item.get_name(), # city name
            subtitle=f'{item.get_parent().get_name()} • {item.get_timezone_str()}' # country name + timezone
        )
        selection_box = Gtk.CheckButton()
        selection_box.add_css_class('selection-mode')
        row.add_suffix(selection_box)
        row.set_activatable_widget(selection_box)
        if self._parent.location and item == self._parent.location:
            selection_box.set_active(True)
            self.active_selection_box = selection_box
        selection_box.connect('toggled', self.location_update_selection, item)
        return row

    def location_update_selection(self, selection_box, item):
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

        self._parent.location = item
        self._parent.config['location'] = (item.serialize(),)

    @Gtk.Template.Callback()
    def location_update_search(self, *args):
        self.settings_filter.changed(Gtk.FilterChange.DIFFERENT)

    def location_filterfunc(self, item, *args):
        try:
            search = self.location_search_entry.get_text()
        except AttributeError:
            return False
        if not search:
            return False
        search = search.lower()

        if search in item.get_name().lower():
            return True
        if item.get_parent().get_name() and search in item.get_parent().get_name().lower():
            return True
        return False

    @Gtk.Template.Callback()
    def open_location_selector(self, *args):
        self.settings_stack.set_visible_child(self.location_selector)

    @Gtk.Template.Callback()
    def close_location_selector(self, *args):
        self.settings_stack.set_visible_child(self.preferences)
