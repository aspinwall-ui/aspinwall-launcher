from gi.repository import Adw, Gtk, GWeather, Gio

@Gtk.Template(resource_path='/org/dithernet/aspinwall/widgets/Weather/ui/weathercontent.ui')
class WeatherContent(Gtk.Box):
    __gtype_name__ = 'WeatherContent'

    content_clamp = Gtk.Template.Child()

    view_switcher = Gtk.Template.Child()
    label_box = Gtk.Template.Child()
    no_location = Gtk.Template.Child()

    weather_condition_icon = Gtk.Template.Child()
    location_name_label = Gtk.Template.Child()
    temperature_label = Gtk.Template.Child()
    weather_condition_label = Gtk.Template.Child()

    attribution_label = Gtk.Template.Child()

    def __init__(self, parent):
        super().__init__()
        self._parent = parent

    def update_data(self, data):
        """Takes a GWeather.Info object and applies the data from it to the widget."""
        location = data.get_location()
        if location:
            self.view_switcher.set_visible_child(self.label_box)
            self.location_name_label.set_label(location.get_name())
        else:
            self.view_switcher.set_visible_child(self.no_location)

        if self._parent.config['temperature-unit'] == 0:
            unit = GWeather.TemperatureUnit.CENTIGRADE
            unit_symbol = 'C'
        elif self._parent.config['temperature-unit'] == 1:
            unit = GWeather.TemperatureUnit.FAHRENHEIT
            unit_symbol = 'F'

        conditions = data.get_conditions()
        if not conditions or conditions == '-':
            conditions = data.get_sky()

        feels_like = None
        feels_like_data = data.get_value_apparent(unit)
        if feels_like_data[0]:
            feels_like = f'Feels like {round(feels_like_data[1],1)}°{unit_symbol}'

        condition_str = [data_bit for data_bit in (conditions, feels_like) if data_bit]

        self.weather_condition_label.set_label(' • '.join(condition_str))
        self.weather_condition_icon.set_from_icon_name(data.get_icon_name())

        self.temperature_label.set_label(f'{round(data.get_value_temp(unit)[1],1)}°{unit_symbol}')

        attribution = data.get_attribution()
        if attribution:
            self.attribution_label.set_visible(True)
            self.attribution_label.set_label(attribution)
            self.content_clamp.set_margin_bottom(0)
        else:
            self.attribution_label.set_visible(False)
            self.content_clamp.set_margin_bottom(12)

@Gtk.Template(resource_path='/org/dithernet/aspinwall/widgets/Weather/ui/settings.ui')
class WeatherSettings(Gtk.Box):
    __gtype_name__ = 'WeatherSettings'

    settings_stack = Gtk.Template.Child()
    preferences = Gtk.Template.Child()
    location_selector = Gtk.Template.Child()

    location_list_box = Gtk.Template.Child()
    location_search_entry = Gtk.Template.Child()

    temperature_unit_selector = Gtk.Template.Child()

    def __init__(self, parent):
        super().__init__()
        self._parent = parent
        self._initialized = False
        self.active_selection_box = None
        self._ignore_sb_active_change = False

        self.temperature_unit_selector.set_selected(parent.config['temperature-unit'])

        self.populate_locations_store()

        self.settings_filter = Gtk.CustomFilter.new(self.location_filterfunc, None)
        self.settings_filterlist = Gtk.FilterListModel.new(
            self.locations_store,
            self.settings_filter
        )
        self.location_list_box.bind_model(self.settings_filterlist, self.location_bind)

        self._initialized = True

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

        self._parent.on_location_changed()

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

    @Gtk.Template.Callback()
    def update_temperature_unit(self, combobox, *args):
        self._parent.config['temperature-unit'] = combobox.get_selected()
        if self._initialized:
            self._parent.refresh()
