# coding: utf-8
"""
Weather widget for Aspinwall
"""
from aspinwall_launcher.widgets import Widget
from aspinwall_launcher.utils.clock import clock_daemon
import gi
gi.require_version('GWeather', '4.0')
from gi.repository import Adw, Gtk, GWeather
translatable = lambda message: message
import gettext

class Weather(Widget):
    metadata = {
        "name": translatable("Weather"),
        "icon": 'weather-clear-symbolic',
        "description": translatable("Shows the current weather forecast."),
        "id": "org.dithernet.aspinwall.widgets.Weather",
        "tags": translatable('weather,forecast'),
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

        Adw.Clamp()
        Adw.ActionRow()
        Adw.ComboRow()

        from .content import WeatherContent, WeatherSettings
        self.content = WeatherContent(self)
        self.set_child(self.content)

        self.settings_container = WeatherSettings(self)
        self.set_settings_child(self.settings_container)

        self.on_location_changed()

    def refresh(self):
        self.weather_data.update()
        self.content.update_data(self.weather_data)

    def on_location_changed(self):
        self.weather_data = GWeather.Info.new(self.location)
        self.weather_data.set_application_id(self.metadata['id'])
        self.weather_data.set_contact_info('abuse@dithernet.org')
        self.weather_data.set_enabled_providers(GWeather.Provider.MET_NO)
        self.weather_data.connect('updated', self.on_data_update)
        self.refresh()

    def on_data_update(self, weather_data, *args):
        self.content.update_data(weather_data)

_widget_class = Weather
