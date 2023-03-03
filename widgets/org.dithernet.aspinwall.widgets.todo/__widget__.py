# coding: utf-8
"""
Simple to-do list plugin for Aspinwall
"""
from aspinwall_launcher.widgets import Widget
from aspinwall_launcher.utils.dimmable import Dimmable
from gi.repository import Adw, Gtk, Gio, GObject
translatable = lambda message: message

class TodoItemBox(Gtk.Box, Dimmable):
    """Represents a single to-do list item."""
    __gtype_name__ = 'TodoItemBox'

    check_button = None
    remove_button = None

    def __init__(self, _parent):
        """Initializes the to-do list item."""
        super().__init__(orientation=Gtk.Orientation.HORIZONTAL, hexpand=True)
        _ = _parent.l
        self._parent = _parent
        self.add_css_class('dimmable')

        self.check_button = Gtk.CheckButton(hexpand=True, halign=Gtk.Align.START)
        self.append(self.check_button)

        self.remove_button = Gtk.Button.new_from_icon_name('list-remove')
        self.remove_button.set_halign(Gtk.Align.END)
        self.remove_button.set_tooltip_text(_('Remove task from list'))
        self.remove_button.add_css_class('flat')
        self.remove_button.connect('clicked', self.remove)
        self.append(self.remove_button)

    def bind_to_item(self, item):
        """Binds to an item."""
        self.item = item
        item.bind_property('name', self.check_button, 'label',
            GObject.BindingFlags.BIDIRECTIONAL | GObject.BindingFlags.SYNC_CREATE
        )
        item.bind_property('checked', self.check_button, 'active',
            GObject.BindingFlags.BIDIRECTIONAL | GObject.BindingFlags.SYNC_CREATE
        )
        item.connect('notify::checked', self.handle_checked)
        self.handle_checked()

    def handle_checked(self, *args):
        """Dim the to-do list item when it's checked."""
        if self.item.props.checked:
            self.dim()
        else:
            self.undim()
        # Workaround for issue where pressing the checkbox would trigger the
        # long-press gesture
        self.set_sensitive(False)
        self.set_sensitive(True)

    def remove(self, *args):
        """Removes the item from the to-do list."""
        self._parent.remove_item(self.item)

class TodoItem(GObject.Object):
    """Represents the data for a to-do list item."""
    __gtype_name__ = 'TodoItem'

    _name = ''
    _checked = False

    def __init__(self, item, todo_widget):
        super().__init__()
        self._todo_widget = todo_widget # keep the widget so that we can save
        self.set_property('name', item[1])
        self.set_property('checked', item[0])

    @GObject.Property(type=bool, default=False)
    def checked(self):
        """Whether the item is ticked off or not."""
        return self._checked

    @checked.setter
    def checked(self, value):
        self._checked = value
        self._todo_widget.save()

    @GObject.Property(type=str)
    def name(self):
        """Whether the item is ticked off or not."""
        return self._name

    @name.setter
    def name(self, value):
        self._name = value
        self._todo_widget.save()

class Todo(Widget):
    metadata = {
        "name": translatable("To-do list"),
        "icon": 'view-list-symbolic',
        "description": translatable("Editable tasks list"),
        "id": "org.dithernet.aspinwall.widgets.Todo",
        "tags": translatable('notes,todo,to do,list'),
        "author": translatable("Aspinwall developers"),
        "url": "https://github.com/aspinwall-ui/aspinwall-launcher",
        "issue_tracker": "https://github.com/aspinwall-ui/aspinwall-launcher/issues",
        "version": "0.0.1"
    }

    has_config = True
    hide_edit_button = True

    def __init__(self, instance=0):
        super().__init__(instance)
        _ = self.l

        self.content = Gtk.Box(hexpand=True, orientation=Gtk.Orientation.VERTICAL)

        # Load to-do list items from config
        self.todo_items = Gio.ListStore(item_type=TodoItem)
        for item in self.config['items']:
            item_object = TodoItem(item, self)
            self.todo_items.append(item_object)

        factory = Gtk.SignalListItemFactory()
        factory.connect('setup', self.list_setup)
        factory.connect('bind', self.list_bind)

        list_container = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        list_scroll = Gtk.ScrolledWindow(
            height_request=230,
            hscrollbar_policy=Gtk.PolicyType.NEVER
        )
        list_scroll.set_child(list_container)

        add_box = Gtk.Box(spacing=6, hexpand=True)
        add_box.set_margin_bottom(6)

        self.new_item_entry = Gtk.Entry(placeholder_text=_('Type in your task...'), hexpand=True)
        self.new_item_entry.set_max_length(96)
        self.new_item_button = Gtk.Button(icon_name='list-add-symbolic', halign=Gtk.Align.END)
        self.new_item_button.connect('clicked', self.add_item)

        add_box.append(self.new_item_entry)
        add_box.append(self.new_item_button)
        self.content.append(add_box)

        self.no_items_status = Adw.StatusPage(
            title=_('No Tasks'),
            description=_('Start by adding a task in the text box above.'),
            icon_name='object-select-symbolic'
        )
        self.no_items_status.add_css_class('compact')
        list_container.append(self.no_items_status)

        self.list_view = Gtk.ListView(
            model=Gtk.SingleSelection(model=self.todo_items), factory=factory
        )
        list_container.append(self.list_view)

        self.todo_items.connect('items-changed', self.update_status)
        self.update_status()

        self.content.append(list_scroll)

        self.set_child(self.content)

    def update_status(self, *args):
        """Shows/hides the 'no tasks' page as needed."""
        if len(list(self.todo_items)) == 0:
            self.list_view.set_visible(False)
            self.no_items_status.set_visible(True)
        else:
            self.list_view.set_visible(True)
            self.no_items_status.set_visible(False)

    def save(self, *args):
        """Saves the contents of the notepad."""
        todo_items = []
        for item in self.todo_items:
            todo_items.append((item.props.checked, item.props.name))
        self.config['items'] = todo_items

    def add_item(self, *args):
        """Adds an item using the data from the new item entry."""
        buffer = self.new_item_entry.get_buffer()
        name = buffer.get_text()
        if name:
            item = [False, name]
            self.todo_items.insert(0, TodoItem(item, self))
            buffer.set_text('', 0)
            self.save()

    def remove_item(self, item):
        """Removes an item from the to-do list."""
        self.todo_items.remove(self.todo_items.find(item)[1])
        self.save()

    def list_setup(self, factory, list_item):
        """Sets up the widget list."""
        list_item.set_child(TodoItemBox(self))

    def list_bind(self, factory, list_item):
        """Binds the list items in the widget list."""
        item_box = list_item.get_child()
        item = list_item.get_item()
        item_box.bind_to_item(item)

_widget_class = Todo
