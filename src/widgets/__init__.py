# coding: utf-8
"""
Contains base class and helper functions for creating widgets.

Code for loading widgets can be found in the loader submodule.
"""
from gi.repository import Adw, Gtk, Gio, GObject
import os
import gettext

class Widget(GObject.GObject):
    """
    Base class for Aspinwall widgets.

    In general, widgets need to define the following variables:
      - metadata - dict containing widget metadata:
                   - name
                   - description
                   - tags (comma-separated string)
                   - thumbnail (url to image)
                   - icon - contains GTK icon name string
      - refresh() - (function) runs in the background at the widget
                    refresh interval
      - content - Widget content. This can be any GTK widget; by default,
                  an empty GtkBox is created.

    For more information, see docs/widgets/creating-widgets.md.
    """
    __gtype_name__ = 'AspWidget'

    metadata = {}
    has_config = False
    has_settings_menu = False
    has_stylesheet = False
    hide_edit_button = False
    schema_base_path = None # set up automatically if not set

    widget_path = None
    instance = None

    def __init__(self, instance=0):
        super().__init__()
        self._container = Adw.Bin(hexpand=True)
        self.instance = instance

        # Set up i18n
        localedir = self.join_with_data_path('po')
        self.l = lambda message: message # noqa: E741
        if os.path.exists(localedir):
            gettext.bindtextdomain(self.id.lower(), localedir)
            self.l = lambda message: gettext.dgettext(self.id.lower(), message) # noqa: E741
            self.metadata['name'] = self.l(self.metadata['name'])
            self.metadata['description'] = self.l(self.metadata['description'])
            self.metadata['tags'] = self.l(self.metadata['tags'])

        # Set up style context, CSS provider
        self.css_class = self.metadata['id'].replace('.', '-')
        self._container.add_css_class(self.css_class)

        self.css_providers = []
        if self.has_stylesheet:
            style_manager = Adw.StyleManager.get_default()
            style_manager.connect('notify::dark', self.theme_update)
            style_manager.connect('notify::high-contrast', self.theme_update)
            self.theme_update(style_manager)

        # Set up config
        if self.has_config:
            self.schema_source = Gio.SettingsSchemaSource.new_from_directory(
                self.join_with_data_path('schemas'),
                Gio.SettingsSchemaSource.get_default(),
                False
            )
            schema = self.schema_source.lookup(self.metadata['id'], False)
            if not schema:
                raise Exception(
                    "Plugin error: schema not found in schema source. Make sure that your schema ID matches the widget ID (note that both are case-sensitive)." # noqa: E501
                )

            if not self.schema_base_path:
                self.schema_base_path = '/' + self.metadata['id'].lower().replace('.', '/') + '/'

            self.config = Gio.Settings.new_full(schema, None, self.schema_base_path + str(instance) + '/')

    def set_child(self, widget):
        """Sets the child widget for the widget."""
        self._container.set_child(widget)

    def join_with_data_path(self, *args):
        """Joins path relative to widget data directory."""
        return os.path.join(os.path.dirname(self.widget_path), *args)

    def refresh(self):
        """(Optional) Runs in the background at the widget refresh interval.
        For more information, see docs/widgets/creating-widgets.md."""
        return None

    def theme_update(self, style_provider, *args):
        """Loads the correct stylesheets for the style provider."""
        for provider in self.css_providers:
            Gtk.StyleContext.remove_provider_for_display(self._container.get_display(), provider)
        self.load_stylesheet_from_file(
            self.join_with_data_path('stylesheet', 'style.css')
        )
        if style_provider.get_dark() and \
                os.path.exists(self.join_with_data_path('stylesheet', 'style-dark.css')):
            self.load_stylesheet_from_file(
                self.join_with_data_path('stylesheet', 'style-dark.css')
            )
            if style_provider.get_high_contrast():
                if os.path.exists(self.join_with_data_path('stylesheet', 'style-hc.css')):
                    self.load_stylesheet_from_file(
                        self.join_with_data_path('stylesheet', 'style-hc.css')
                    )

                if os.path.exists(self.join_with_data_path('stylesheet', 'style-hc-dark.css')):
                    self.load_stylesheet_from_file(
                        self.join_with_data_path('stylesheet', 'style-hc-dark.css')
                    )
        else:
            if style_provider.get_high_contrast() and \
                    os.path.exists(self.join_with_data_path('stylesheet', 'style-hc.css')):
                self.load_stylesheet_from_file(
                    self.join_with_data_path('stylesheet', 'style-hc.css')
                )

    def load_stylesheet_from_string(self, string):
        """Loads a stylesheet from a string."""

        # HACK: In order to make life easier, and make hijacking the launcher's CSS a bit
        # more difficult, we do a little hack here that prefixes every rule with a class
        # specific to the widget.
        #
        # Previously this was done using Gtk.StyleContext.add_provider, but there were
        # two issues with it:
        #  - It's due to be deprecated in GTK 4.10.
        #  - It didn't work. Like, at all. And it took me far too long to realize.
        # I'm assuming the way it was meant to be used was by having an individual CSS
        # file for every element(!), or maybe there's also a prefix approach needed
        # like the one we're doing here.
        #
        # This is a bit error-prone and I wish there was a different way to do it, but
        # I doubt upstream would be interested (this is an *incredibly* niche use case).
        # Might be worth asking though?

        rules_split = [ rule.replace('\n', '') + '}' for rule in string.split('}') if rule.replace('\n', '') ]
        rules = ''
        for rule in rules_split:
            if not rule:
                continue
            if '{' in rule:
                rules += f' .{self.css_class} '
            rules += rule

        self.css_providers.append(Gtk.CssProvider())
        self.css_providers[-1].load_from_data(bytes(rules, 'ascii'))
        Gtk.StyleContext.add_provider_for_display(
            self._container.get_display(),
            self.css_providers[-1],
            Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION + len(self.css_providers)
        )

    def load_stylesheet_from_file(self, path):
        """Loads a stylesheet from a file."""
        with open(path, 'r') as css_file:
            self.load_stylesheet_from_string(css_file.read())

    @GObject.Property
    def id(self):
        """The ID of the widget, as defined in its metadata."""
        return self.metadata['id']

    @GObject.Property
    def name(self):
        """The name of the widget, as defined in its metadata."""
        return self.metadata['name']

    @GObject.Property
    def icon_name(self):
        """The icon name of the widget, as defined in its metadata."""
        return self.metadata['icon']

    @GObject.Property
    def description(self):
        """The description of the widget, as defined in its metadata."""
        return self.metadata['description']

    @GObject.Property
    def tags(self):
        """The tags of the widget, as defined in its metadata."""
        return self.metadata['tags'].split(',')
