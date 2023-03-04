# coding: utf-8
"""
Contains code for the widget chooser and widget infoboxes for the chooser.
"""
from gi.repository import Adw, Gtk, Gio, GLib, GObject

from .widgetmanager import widget_manager
from ..widgets.data import WidgetData
from ..widgets.loader import available_widgets
from ..widgets.package import WidgetPackage

@Gtk.Template(resource_path='/org/dithernet/aspinwall/launcher/ui/widgetinstalldialog.ui')
class WidgetInstallDialog(Adw.MessageDialog):
    """
    Dialog that appears when installing a new widget.
    """
    __gtype_name__ = 'WidgetInstallDialog'

    icon = Gtk.Template.Child()
    name = Gtk.Template.Child()
    author = Gtk.Template.Child()
    version = Gtk.Template.Child()

    def __init__(self, package, chooser):
        super().__init__(modal=True, transient_for=chooser.get_native())
        self.package = package
        self.chooser = chooser

        for widget in chooser.store:
            if widget.id == package.id:
                if widget.version == package.version:
                    self.set_heading("Reinstall this widget?")
                    self.set_response_label("install", "_Reinstall")
                else:
                    self.set_heading("Upgrade this widget?")
                    self.set_response_label("install", "_Upgrade")
                break

        self.package.bind_property('icon_name', self.icon, 'icon_name',
            GObject.BindingFlags.SYNC_CREATE)
        self.package.bind_property('name', self.name, 'label',
            GObject.BindingFlags.SYNC_CREATE)
        self.package.bind_property('author', self.author, 'label',
            GObject.BindingFlags.SYNC_CREATE)
        self.package.bind_property('version', self.version, 'label',
            GObject.BindingFlags.SYNC_CREATE)

    @Gtk.Template.Callback()
    def handle_response(self, dialog, response):
        if response == 'install':
            self.package.install()
        self.close()

@Gtk.Template(resource_path='/org/dithernet/aspinwall/launcher/ui/widgetinfobox.ui')
class WidgetInfobox(Gtk.Box):
    """
    Infobox for widgets displayed in the widget chooser dialog.
    """
    __gtype_name__ = 'WidgetInfobox'

    widget_icon = Gtk.Template.Child('widget_infobox_icon')
    widget_name = Gtk.Template.Child('widget_infobox_name')
    widget_description = Gtk.Template.Child('widget_infobox_description')

    def __init__(self):
        """Initializes a widget infobox."""
        super().__init__()

        # Needed to recognize gestures; we don't actually do anything with it here,
        # but it is used by clickout in the window
        self.clickin_gesture = Gtk.GestureClick()
        self.add_controller(self.clickin_gesture)

    def bind_to_widget(self, widget_data):
        """Binds the infobox to a widget."""
        self.widget_data = widget_data

        self.widget_icon.set_from_icon_name(widget_data.metadata['icon'])
        self.widget_name.set_markup(
            '<span size="large" font="bold">' + widget_data.metadata['name'] + '</span>'
        )
        self.widget_description.set_markup(
            '<span size="medium">' + widget_data.metadata['description'] + '</span>'
        )

    @Gtk.Template.Callback()
    def add_widget_from_infobox(self, *args):
        """Adds the widget to the widget box."""
        widget_manager.add_widget_by_class(self.widget_data.widget_class)

    @Gtk.Template.Callback()
    def about_widget_from_infobox(self, *args):
        """Shows the About window for the widget."""
        self.widget_data.show_about_window(self.get_native())

@Gtk.Template(resource_path='/org/dithernet/aspinwall/launcher/ui/widgetchooser.ui')
class WidgetChooser(Gtk.Box):
    """Widget chooser widget."""
    __gtype_name__ = 'WidgetChooser'

    widget_list = Gtk.Template.Child()
    search = Gtk.Template.Child()
    no_results = Gtk.Template.Child()

    def __init__(self):
        """Initializes a widget chooser."""
        super().__init__()

        factory = Gtk.SignalListItemFactory()
        factory.connect('setup', self.setup)
        factory.connect('bind', self.bind)

        # Set up model and factory
        self.store = Gio.ListStore(item_type=WidgetData)
        for widget_class in available_widgets:
            self.store.append(WidgetData(widget_class))

        # Set up sort model
        self.sort_model = Gtk.SortListModel(model=self.store)
        self.sorter = Gtk.CustomSorter.new(self.sort_func, None)
        self.sort_model.set_sorter(self.sorter)

        # Set up filter model
        filter_model = Gtk.FilterListModel(model=self.sort_model)
        self.filter = Gtk.CustomFilter.new(self.filter_by_name, filter_model)
        filter_model.set_filter(self.filter)
        self.search.connect('search-changed', self.search_changed)

        self.model = filter_model

        # Set up widget list
        self.widget_list.set_model(Gtk.NoSelection(model=self.model))
        self.widget_list.set_factory(factory)

        # Set up file filter for widget install dialog
        self.widget_pkg_filter = Gtk.FileFilter()
        for mime in ('application/gzip', 'application/x-gzip', 'application/tar+gzip'):
            self.widget_pkg_filter.add_mime_type(mime)
        self.file_chooser = None

    def show(self, *args):
        self.get_parent().set_reveal_flap(True)
        window = self.get_native()
        window.wallpaper.dim()
        window.clockbox.dim()

        window.app_chooser_button_revealer.set_sensitive(False)
        window.widgetbox.chooser_button_revealer.set_sensitive(False)

        self.search.grab_focus()

    def setup(self, factory, list_item):
        """Sets up the widget list."""
        list_item.set_child(WidgetInfobox())

    def update_model(self):
        """Updates the widget list model."""
        self.store = Gio.ListStore(item_type=WidgetData)
        for widget in available_widgets:
            self.store.append(WidgetData(widget))

        self.sort_model.set_model(self.store)

    def bind(self, factory, list_item):
        """Binds the list items in the widget list."""
        widget_infobox = list_item.get_child()
        widget = list_item.get_item()
        widget_infobox.bind_to_widget(widget)

    def filter_by_name(self, widget, user_data):
        """Fill-in for custom filter for widget list."""
        query = self.search.get_text()
        if not query:
            return True
        query = query.casefold()

        if query in widget.name.casefold():
            return True

        for tag in widget.tags:
            if query in tag.casefold():
                return True

        return False

    def sort_func(self, a, b, *args):
        """Sort function for the widget list sorter."""
        a_name = GLib.utf8_casefold(a.name, -1)
        if not a_name:
            a_name = ''
        b_name = GLib.utf8_casefold(b.name, -1)
        if not b_name:
            b_name = ''
        return GLib.utf8_collate(a_name, b_name)

    def search_changed(self, *args):
        """Notifies the filter about search changes."""
        self.filter.changed(Gtk.FilterChange.DIFFERENT)

        if self.model.get_n_items() == 0:
            self.no_results.set_visible(True)
        else:
            self.no_results.set_visible(False)

        # TODO: Scroll back to start of list

    @Gtk.Template.Callback()
    def hide(self, *args):
        """Hides the widget chooser."""
        self.get_parent().set_reveal_flap(False)
        window = self.get_native()
        if not window.widgetbox.management_mode:
            window.wallpaper.undim()
            window.clockbox.undim()
        window.app_chooser_button_revealer.set_sensitive(True)
        window.widgetbox.chooser_button_revealer.set_sensitive(True)

    @Gtk.Template.Callback()
    def show_package_file_selector(self, *args):
        """
        Shows the widget package file selector for selecting a widget to
        install.
        """
        if self.file_chooser:
            return

        self.file_chooser = Gtk.FileChooserNative(
                                # TRANSLATORS: Title of window for opening package
                                title=_("Open package file"),
                                transient_for=self.get_native(),
                                action=Gtk.FileChooserAction.OPEN,
                                select_multiple=True
                                )

        self.file_chooser.set_filter(self.widget_pkg_filter)

        self.file_chooser.connect('response', self.open_pkg_from_dialog)
        self.file_chooser.show()

    def open_pkg_from_dialog(self, dialog, response):
        """
        Callback for a FileChooser that takes the response and opens the
        package selected in the dialog.
        """
        self.file_chooser.destroy()
        self.file_chooser = None
        if response == Gtk.ResponseType.ACCEPT:
            window = self.get_native()
            try:
                package = WidgetPackage(dialog.get_file().get_path())
            except ValueError as e:
                toast = Adw.Toast.new(f"Malformed package: {e}")
                window.widgetbox.toast_overlay.add_toast(toast)
            install_dialog = WidgetInstallDialog(package, self)
            install_dialog.present()
