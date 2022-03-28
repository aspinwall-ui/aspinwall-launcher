# coding: utf-8
"""
Contains generic code for notification lists, as well as the code for the
notification list popup.
"""
from gi.repository import Gtk
import time
import threading

from aspinwall.shell.notificationbox import NotificationListView # noqa: F401
from aspinwall.shell.surface import Surface

@Gtk.Template(resource_path='/org/dithernet/aspinwall/shell/ui/notificationpopup.ui')
class NotificationPopup(Surface):
	"""
	Notification popup surface that shows new notifications as they
	are received.
	"""
	__gtype_name__ = 'NotificationPopup'

	notification_list = Gtk.Template.Child()

	def __init__(self, app):
		"""Initializes the notification popup."""
		super().__init__(
			application=app,
			visible=False,
			halign=Gtk.Align.CENTER,
			valign=Gtk.Align.START
		)

		self.connect('notify::monitor-width', self.update_popup_size)
		self.connect('notify::monitor-height', self.update_popup_size)
		self.connect('map', self.update_popup_size)

		# Set up recent notification filter
		if not self.notification_list.notification_store:
			return

		self.filter_model = Gtk.FilterListModel(model=self.notification_list.notification_store)
		self.filter = Gtk.CustomFilter.new(self.filter_by_time, self.filter_model)
		self.filter_model.set_filter(self.filter)

		# Start a thread to refresh the filter every second
		filter_thread = threading.Thread(target=self.filter_updater_func, daemon=True)
		filter_thread.start()

		self.notification_list.set_model(Gtk.SingleSelection(model=self.filter_model))

		self.notification_list.notification_interface.daemon.sorter.connect(
			'changed', self.update_filter
		)
		self.filter_model.connect('items-changed', self.show_or_hide)

	def update_popup_size(self, *args):
		"""Updates the size of the notification popup."""
		self.set_width(self.monitor_width / 4)

	def filter_by_time(self, notification, *args):
		"""Discards notifications older than a certain treshold."""
		treshold = time.time() - 5
		if notification._time_received <= treshold:
			return False
		return True

	def show_or_hide(self, store, *args):
		if store.get_n_items() > 0:
			self.set_visible(True)
		else:
			self.set_visible(False)

	def update_filter(self, *args):
		"""Callback function that forces a filter refresh."""
		self.filter.changed(Gtk.FilterChange.DIFFERENT)

	def filter_updater_func(self):
		"""Updates the filter every second."""
		while True:
			self.filter.changed(Gtk.FilterChange.DIFFERENT)
			time.sleep(1)
