# coding: utf-8
"""
Contains code for the app chooser.
"""
from gi.repository import Gdk, GLib, Gio, Gtk, GdkPixbuf

from ..config import config

# Used by AppIcon to find the app chooser revealer
app_chooser = None

def app_info_to_filenames(appinfo):
    """Takes a list of apps and returns their filenames."""
    output = {}
    for app in appinfo:
        output[app.get_filename()] = app
    return output

@Gtk.Template(resource_path='/org/dithernet/aspinwall/launcher/ui/appicon.ui')
class AppIcon(Gtk.Box):
    """Contains an app icon for the app chooser."""
    __gtype_name__ = 'AppIcon'

    app_icon = Gtk.Template.Child()
    app_name = Gtk.Template.Child()

    popover = Gtk.Template.Child()
    appicon_fav_menu = Gtk.Template.Child()
    appicon_notfav_menu = Gtk.Template.Child()

    actions_installed = False

    def __init__(self):
        """Initializes an AppIcon."""
        if not AppIcon.actions_installed:
            self.install_action('favorite', None, self.favorite)
            self.install_action('unfavorite', None, self.unfavorite)
            AppIcon.actions_installed = True
        super().__init__()
        self.longpress_gesture = None
        #self.popover.present()
        self.connect('map', self.setup_controller)
        self.connect('unmap', self.dismantle_controller)
        self.connect('destroy', self.dismantle_controller)

    def setup_controller(self, *args):
        if not self.longpress_gesture:
            self.longpress_gesture = Gtk.GestureLongPress(propagation_phase=Gtk.PropagationPhase.CAPTURE)
            self.longpress_gesture.connect('pressed', self.show_menu)
            self.add_controller(self.longpress_gesture)

    def dismantle_controller(self, *args):
        if self.longpress_gesture:
            self.remove_controller(self.longpress_gesture)
            self.longpress_gesture = None

    def favorite(self, app_icon, *args):
        """Adds the app to favorites."""
        if app_icon.app_filename not in config['favorite-apps']:
            new_list = config['favorite-apps'].copy()
            new_list.append(app_icon.app_filename)
            config['favorite-apps'] = new_list
            self.is_favorite = True

            app_chooser.filter.changed(Gtk.FilterChange.MORE_STRICT)
            app_chooser.favorites_filter.changed(Gtk.FilterChange.LESS_STRICT)

            if not app_chooser.in_search:
                app_chooser.favorites_revealer.set_reveal_child(True)

    def unfavorite(self, app_icon, *args):
        """Removes the app from favorites."""
        if app_icon.app_filename in config['favorite-apps']:
            new_list = config['favorite-apps'].copy()
            new_list.remove(app_icon.app_filename)
            config['favorite-apps'] = new_list
            self.is_favorite = False

            app_chooser.filter.changed(Gtk.FilterChange.LESS_STRICT)
            app_chooser.favorites_filter.changed(Gtk.FilterChange.MORE_STRICT)

            if not new_list:
                app_chooser.favorites_revealer.set_reveal_child(False)

    def show_menu(self, event_controller, *args):
        """Shows the app icon menu."""
        if self.is_favorite:
            self.popover.set_menu_model(self.appicon_fav_menu)
        else:
            self.popover.set_menu_model(self.appicon_notfav_menu)
            if len(config['favorite-apps']) >= 4:
                self.action_set_enabled('favorite', False)
            else:
                self.action_set_enabled('favorite', True)
        self.popover.show()

@Gtk.Template(resource_path='/org/dithernet/aspinwall/launcher/ui/appchooser.ui')
class AppChooser(Gtk.Box):
    """App chooser widget."""
    __gtype_name__ = 'AppChooser'

    # Whether we are currently searching or not
    in_search = False

    app_grid = Gtk.Template.Child()
    app_grid_container = Gtk.Template.Child()
    app_grid_status_stack = Gtk.Template.Child()
    favorites_revealer = Gtk.Template.Child()
    favorites_grid = Gtk.Template.Child()
    search = Gtk.Template.Child()
    no_results = Gtk.Template.Child()

    def __init__(self):
        """Initializes an app chooser."""
        super().__init__()

        # Set up factory for app icons
        factory = Gtk.SignalListItemFactory()
        factory.connect('setup', self.setup)
        factory.connect('bind', self.bind)

        # Set up store for app model
        self.store = Gio.ListStore(item_type=Gio.AppInfo)
        self.fill_model()

        # Set up sort model
        self.sort_model = Gtk.SortListModel(model=self.store)
        self.sorter = Gtk.CustomSorter.new(self.sort_func, None)
        self.sort_model.set_sorter(self.sorter)

        # Set up filter model
        filter_model = Gtk.FilterListModel(model=self.sort_model)
        self.filter = Gtk.CustomFilter.new(self.filter_by_name, filter_model)
        filter_model.set_filter(self.filter)
        self.search.connect('search-changed', self.search_changed)

        # Set up favorites model
        self.favorites_model = Gtk.FilterListModel(model=self.store)
        self.favorites_filter = Gtk.CustomFilter.new(
            self.is_favorite,
            self.favorites_model
        )
        self.favorites_model.set_filter(self.favorites_filter)

        self.model = filter_model

        # Set up app grid
        self.selection_model = Gtk.SingleSelection(model=self.model)
        self.app_grid.set_model(self.selection_model)
        self.app_grid.set_factory(factory)

        # Set up favorites grid
        self.favorites_grid.set_model(Gtk.NoSelection(model=self.favorites_model))
        self.favorites_grid.set_factory(factory)

        # Show/hide the favorites depending on whether there are any
        if config['favorite-apps']:
            self.favorites_revealer.set_reveal_child(True)
        else:
            self.favorites_revealer.set_reveal_child(False)

        self.late_init_done = False
        self.connect('realize', self.late_init)

        global app_chooser
        app_chooser = self

    def late_init(self, *args):
        if not self.late_init_done:
            surface = self.get_native().get_surface()
            surface.connect('layout', self.handle_resize)
            self.handle_resize(surface, surface.get_width(), surface.get_height())
            self.late_init_done = True

    def handle_resize(self, surface, width, height, *args):
        """Workarounds for scaling."""
        for grid in [self.app_grid, self.favorites_grid]:
            if width <= 600:
                if width >= 375:
                    grid.add_css_class('small-icons')
                    grid.remove_css_class('smaller-icons')
                    grid.set_min_columns(3)
                    grid.set_max_columns(3)
                else:
                    grid.add_css_class('smaller-icons')
                    grid.remove_css_class('small-icons')
                    grid.set_min_columns(2)
                    grid.set_max_columns(2)
            else:
                grid.set_min_columns(4)
                grid.set_max_columns(4)
                if grid == self.favorites_grid:
                    grid.add_css_class('small-icons')
                else:
                    grid.remove_css_class('small-icons')
                grid.remove_css_class('smaller-icons')
            grid.set_visible(True)

    def setup(self, factory, list_item):
        """Sets up the app list."""
        list_item.set_child(AppIcon())

    def bind(self, factory, list_item):
        """Binds the list items in the app list."""
        app_icon = list_item.get_child()
        app = list_item.get_item()

        # The following code is here to work around a bizzare bug I encountered
        # where some SVGs would completely fail to load, segfaulting the entire
        # program. This is a lazy fix that loads the icons manually in most cases,
        # which should hopefully be enough to work around the issue.
        icon_found = False
        icon_name = app.get_icon().to_string()
        if '/' in icon_name:
            try:
                app_icon.app_icon.set_from_pixbuf(
                    GdkPixbuf.Pixbuf.new_from_file_at_scale(
                        icon_name, 96, 96, True
                    )
                )
            except GLib.GError:
                pass
            else:
                icon_found = True
        elif '.' not in icon_name:
            app_icon.app_icon.set_from_icon_name(icon_name)
            icon_found = True
        else:
            icon_paths = Gtk.IconTheme.get_for_display(self.get_display()).get_search_path()
            for path in ['/usr/share/icons/hicolor/scalable/apps'] + icon_paths:
                try:
                    app_icon.app_icon.set_from_pixbuf(
                        GdkPixbuf.Pixbuf.new_from_file_at_scale(
                            path + '/' + icon_name + '.svg', 96, 96, True
                        )
                    )
                except GLib.GError:
                    try:
                        app_icon.app_icon.set_from_pixbuf(
                            GdkPixbuf.Pixbuf.new_from_file_at_scale(
                                path + '/' + icon_name + '.png', 96, 96, True
                            )
                        )
                    except GLib.GError:
                        continue
                    else:
                        icon_found = True
                        break
                else:
                    icon_found = True
                    break

        if not icon_found:
            app_icon.app_icon.set_from_icon_name(icon_name)

        app_icon.app_name.set_label(app.get_name())

        if app.get_filename() in config['favorite-apps']:
            app_icon.is_favorite = True
        else:
            app_icon.is_favorite = False

        app_icon.app_filename = app.get_filename()

    @Gtk.Template.Callback()
    def activate(self, grid, position, *args):
        """Opens the app represented by the app icon."""
        app = grid.get_model().get_item(position)
        context = Gdk.Display.get_app_launch_context(self.get_display())
        app.launch(None, context)
        self.hide()

    def fill_model(self):
        """Fills the favorites and app grid models."""
        appinfo = Gio.AppInfo.get_all()
        self.store.remove_all()

        filenames = []

        for app in appinfo:
            if not Gio.AppInfo.should_show(app):
                continue
            self.store.append(app)
            filenames.append(app.get_filename())

        # Delete missing .desktop entries in favorite apps
        favs_output = config['favorite-apps'].copy()
        for file in config['favorite-apps']:
            if file not in filenames:
                favs_output.remove(file)
        if config['favorite-apps'] != favs_output:
            config['favorite-apps'] = favs_output

        self.previous_appinfo = self.store

    def update_model(self):
        """Updates the app grid model."""
        _appinfo = Gio.ListStore(item_type=Gio.AppInfo)
        for app in Gio.AppInfo.get_all():
            if app.should_show():
                _appinfo.append(app)

        appinfo = app_info_to_filenames(_appinfo)
        previous_appinfo = app_info_to_filenames(self.previous_appinfo)

        # Comparing the stores to each other erroneously returns True
        if previous_appinfo.keys() != appinfo.keys():
            new_appinfo = list(set(previous_appinfo.keys()) - set(appinfo.keys())) + \
                list(set(appinfo.keys()) - set(previous_appinfo.keys()))
            for app_name in new_appinfo:
                if app_name in previous_appinfo:
                    # App removed
                    find = self.store.find(previous_appinfo[app_name])
                    if find[0]:
                        self.store.remove(find[1])
                    if app_name in config['favorite-apps']:
                        new_list = config['favorite-apps'].copy()
                        new_list.remove(app_name)
                        config['favorite-apps'] = new_list
                    self.sorter.changed(Gtk.SorterChange.DIFFERENT)
                    self.filter.changed(Gtk.FilterChange.DIFFERENT)
                    self.favorites_filter.changed(Gtk.FilterChange.DIFFERENT)
                else:
                    # App added
                    self.store.append(appinfo[app_name])
                    self.sorter.changed(Gtk.SorterChange.DIFFERENT)
                    self.filter.changed(Gtk.FilterChange.DIFFERENT)
                    self.favorites_filter.changed(Gtk.FilterChange.DIFFERENT)

        if config['favorite-apps'] and not self.in_search:
            self.favorites_revealer.set_reveal_child(True)
        else:
            self.favorites_revealer.set_reveal_child(False)

    def filter_by_name(self, appinfo, user_data):
        """Fill-in for custom filter for app grid."""
        query = self.search.get_text()
        if not query:
            if appinfo.get_filename() in config['favorite-apps']:
                return False
            return True
        query = query.casefold()

        if query in appinfo.get_name().casefold():
            return True

        if appinfo.get_generic_name():
            if query in appinfo.get_generic_name().casefold():
                return True

        for keyword in appinfo.get_keywords():
            if query in keyword.casefold():
                return True

        return False

    def is_favorite(self, appinfo, *args):
        """
        Takes a Gio.AppInfo and returns whether the app is in favorites or not.
        """
        if appinfo.get_filename() in config['favorite-apps']:
            return True
        return False

    def sort_func(self, a, b, *args):
        """Sort function for the app grid icon sorter."""
        a_name = GLib.utf8_casefold(a.get_name(), -1)
        if not a_name:
            a_name = ''
        b_name = GLib.utf8_casefold(b.get_name(), -1)
        if not b_name:
            b_name = ''
        return GLib.utf8_collate(a_name, b_name)

    def search_changed(self, search_entry, *args):
        """Notifies the filter about search changes."""
        if search_entry.get_text():
            self.in_search = True
            self.favorites_revealer.set_reveal_child(False)
        else:
            self.in_search = False
            if config['favorite-apps']:
                self.favorites_revealer.set_reveal_child(True)
            self.app_grid_status_stack.set_visible_child_name('app-grid')

        self.filter.changed(Gtk.FilterChange.DIFFERENT)

        if self.model.get_n_items() == 0:
            self.app_grid_status_stack.set_visible_child_name('no-results')
        else:
            self.app_grid_status_stack.set_visible_child_name('app-grid')

        # Select first item in list
        self.selection_model.select_item(0, True)

        # TODO: Scroll back to the top. Currently we can't do this, because the
        # gridview scroll position lags behind the scrollbar position.

    @Gtk.Template.Callback()
    def hide(self, *args):
        """Hides the app chooser."""
        self.get_parent().set_visible_child_name('content')
        self.get_native().pause_focus_manager = False
