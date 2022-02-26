# coding: utf-8
"""
Contains code for the widget chooser and widget infoboxes for the chooser.
"""
from gi.repository import Gtk, Gio, GLib

from aspinwall.widgets.data import WidgetData
from aspinwall.widgets.loader import available_widgets

# Pointer to the widget box; set up by the WidgetBox __init__ function,
# required by the widget chooser as the widget addition target
# This is defined in this file and set externally to avoid circular imports.
widgetbox = None

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
		widgetbox.add_widget(self.widget_data.widget_class)

@Gtk.Template(resource_path='/org/dithernet/aspinwall/launcher/ui/widgetchooser.ui')
class WidgetChooser(Gtk.Revealer):
	"""Widget chooser widget."""
	__gtype_name__ = 'WidgetChooser'

	widget_list = Gtk.Template.Child()
	search = Gtk.Template.Child()

	def __init__(self):
		"""Initializes a widget chooser."""
		super().__init__()

		factory = Gtk.SignalListItemFactory()
		factory.connect('setup', self.setup)
		factory.connect('bind', self.bind)

		# Set up model and factory
		store = Gio.ListStore(item_type=WidgetData)
		for widget_class in available_widgets:
			store.append(WidgetData(widget_class))

		# Set up sort model
		self.sort_model = Gtk.SortListModel(model=store)
		self.sorter = Gtk.CustomSorter.new(self.sort_func, None)
		self.sort_model.set_sorter(self.sorter)

		# Set up filter model
		filter_model = Gtk.FilterListModel(model=self.sort_model)
		self.filter = Gtk.CustomFilter.new(self.filter_by_name, filter_model)
		filter_model.set_filter(self.filter)
		self.search.connect('search-changed', self.search_changed)

		self.model = filter_model

		# Set up widget list
		self.widget_list.set_model(Gtk.SingleSelection(model=self.model))
		self.widget_list.set_factory(factory)

	def setup(self, factory, list_item):
		"""Sets up the widget list."""
		list_item.set_child(WidgetInfobox())

	def update_model(self):
		"""Updates the widget list model."""
		store = Gio.ListStore(item_type=WidgetData)
		for widget in available_widgets:
			store.append(WidgetData(widget))

		self.sort_model.set_model(store)

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
		# Select first item in list
		selection_model = self.widget_list.get_model()
		selection_model.set_selected(0)
		# TODO: Scroll back to top of list

	@Gtk.Template.Callback()
	def hide(self, *args):
		"""Hides the widget chooser."""
		self.set_reveal_child(False)
