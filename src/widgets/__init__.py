# coding: utf-8
"""
Contains base class and helper functions for creating widgets.

Code for loading widgets can be found in the loader submodule.
"""
from gi.repository import Adw, Gtk, Gio, GObject
import os
import gettext
import re

class Widget(GObject.GObject):
    """
    Base class for Aspinwall widgets.

    In general, widgets need to define the following variables:
      - metadata - dict containing widget metadata:
                   - name
                   - description
                   - author
                   - version
                   - tags (comma-separated string)
                   - thumbnail (url to image)
                   - icon - contains GTK icon name string
                   - url - link to repository, if applicable
                   - issue_tracker - link to issue tracker, if applicable
      - refresh() - (function) runs in the background at the widget
                    refresh interval

    For more information, see docs/widgets/creating-widgets.md.
    """
    __gtype_name__ = 'AspWidget'

    metadata = {}
    has_config = False
    has_settings_menu = False
    has_stylesheet = False
    has_gresource = False
    hide_edit_button = False
    schema_base_path = None # set up automatically if not set

    widget_path = None
    instance = None

    def __init__(self, instance=0):
        super().__init__()
        self._container = Adw.Bin(hexpand=True)
        if self.has_settings_menu:
            self._settings_container = Adw.Bin(hexpand=True)
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
        self.loaded_stylesheets = []
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
            self.settings_schema = self.schema_source.lookup(self.metadata['id'], False)
            if not self.settings_schema:
                raise Exception(
                    "Plugin error: schema not found in schema source. Make sure that your schema ID matches the widget ID (note that both are case-sensitive)." # noqa: E501
                )

            if not self.schema_base_path:
                self.schema_base_path = '/' + self.metadata['id'].lower().replace('.', '/') + '/'

            self.config = Gio.Settings.new_full(self.settings_schema, None, self.schema_base_path + str(instance) + '/')

        # Set up GResource
        if self.has_gresource:
            self.gresource = Gio.Resource.load(self.join_with_data_path(self.id + '.gresource'))
            self.gresource._register()

    def destroy(self):
        """Cleans up after the widget is removed."""
        if self.has_config:
            for key in self.settings_schema.list_keys():
                self.config.reset(key)

        if self.has_gresource:
            self.gresource._unregister()

    def set_child(self, widget):
        """Sets the child widget for the widget."""
        self._container.set_child(widget)

    def set_settings_child(self, widget):
        """Sets the settings child widget for the widget."""
        if not self.has_settings_menu:
            raise ValueError("Trying to set settings child, but has_settings is not True")
        self._settings_container.set_child(widget)

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
        self.loaded_stylesheets = []
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

    def _prepare_stylesheet_string(self, string, import_base=None):
        if not import_base:
            import_base = self.join_with_data_path('stylesheet')

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

        # Remove comments (both for minification reasons and for breakage prevention)
        _string_clean = re.sub('/\*[^*]*\*+([^/][^*]*\*+)*/', '', string)

        rules_split = [ rule.replace('\n', '') for rule in _string_clean.split('}') if rule.replace('\n', '') ] # noqa: E501
        rules = ''
        for rule in rules_split:
            if not rule:
                continue

            # Correctly handle defines and imports
            if '@' in rule:
                if '{' in rule:
                    customs = rule.split('{')[0].split(';')
                else:
                    customs = rule.split(';')
                # Defines/imports are tricky since they're essentially properties
                # outside of a rule; since we only guess the boundaries of a rule
                # based on the position of curly brackets (}), it's easy to lead to
                # a scenario where the class is prepended to the define instead of
                # the selector.
                #
                # This works around it by splitting out the individual defines,
                # then only applying the class to the selector that's left.
                n = 0
                for cust in customs:
                    if n == len(customs) - 1 and len(rule.split('{')) > 1 and \
                            rule.split('{')[1].replace(' ', ''):
                        rules += f' .{self.css_class} {cust} '
                        break
                    if '@import' in cust:
                        import_filename = re.findall(r"['\"](.*?)['\"]", cust)[0]
                        import_path = os.path.join(import_base, import_filename)
                        if import_path in self.loaded_stylesheets:
                            print(f"ERROR: Potential circular import in stylesheet found (trying to load {import_path} which is already loaded)") # noqa: E501
                        else:
                            self.loaded_stylesheets.append(import_path)
                            with open(import_path, 'r') as import_file:
                                raw_import = import_file.read()
                            rules += ' ' + self._prepare_stylesheet_string(raw_import) + ' '
                    elif cust.replace(' ', ''):
                        rules += cust + ';'
                    n += 1
                if '{' in rule and len(rule.split('{')) > 1 and rule.split('{')[1].replace(' ', ''):
                    rules += '{ ' + rule.split('{')[1] + '}'
            else:
                if '{' in rule:
                    rules += f' .{self.css_class} ' + rule + '}'

        return rules

    def load_stylesheet_from_string(self, string, import_base=None):
        """Loads a stylesheet from a string."""
        rules = self._prepare_stylesheet_string(string, import_base)

        self.css_providers.append(Gtk.CssProvider())
        self.css_providers[-1].load_from_data(bytes(rules, 'utf-8'))
        Gtk.StyleContext.add_provider_for_display(
            self._container.get_display(),
            self.css_providers[-1],
            Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION + len(self.css_providers)
        )

    def load_stylesheet_from_file(self, path):
        """Loads a stylesheet from a file."""
        if path in self.loaded_stylesheets:
            print(f"ERROR: Potential circular import in stylesheet found (trying to load {path} which is already loaded)") # noqa: E501
            return False
        self.loaded_stylesheets.append(path)
        with open(path, 'r') as css_file:
            self.load_stylesheet_from_string(css_file.read(), os.path.dirname(path))

    def show_about_window(self, transient_for=None):
        """Displays an about window based on the metadata of the widget."""
        about_window = Adw.AboutWindow(
            application_name=self.metadata['name'],
            application_icon=self.metadata['icon'],
            developer_name=self.metadata['author'],
            version=self.metadata['version']
        )

        if 'url' in self.metadata:
            about_window.set_website(self.metadata['url'])
        if 'issue_tracker' in self.metadata:
            about_window.set_issue_url(self.metadata['issue_tracker'])

        if transient_for:
            about_window.set_transient_for(transient_for)
            about_window.set_modal(True)

        about_window.present()

    @GObject.Property
    def id(self):
        """The ID of the widget, as defined in its metadata."""
        return self.metadata['id']

    @GObject.Property
    def version(self):
        """The version of the widget, as defined in its metadata."""
        return self.metadata['version']

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
    def author(self):
        """The author of the widget, as defined in its metadata."""
        return self.metadata['author']

    @GObject.Property
    def tags(self):
        """The tags of the widget, as defined in its metadata."""
        return self.metadata['tags'].split(',')

    @GObject.Property
    def url(self):
        """
        A link to the repository/website of the widget, as defined in its metadata.

        This value can be null.
        """
        return self.metadata['url']

    @GObject.Property
    def issue_tracker(self):
        """
        A link to the issue tracker of the widget, as defined in its metadata.

        This value can be null.
        """
        return self.metadata['issue_tracker']
