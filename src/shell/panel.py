# coding: utf-8
"""
Contains the code for the panel.
"""
from gi.repository import Gdk, GdkX11, Gtk
from Xlib.xobject.drawable import Window
from Xlib.protocol.display import Display

@Gtk.Template(resource_path='/org/dithernet/aspinwall/shell/ui/panel.ui')
class Panel(Gtk.Window):
	"""The status bar on the top of the screen."""
	__gtype_name__ = 'Panel'

	def __init__(self, app):
		"""Initializes the panel."""
		super().__init__(application=app)

		self.show()

		monitor = Gdk.Display.get_default().get_monitor_at_surface(
			self.get_surface()
		)
		self.set_size_request(monitor.get_geometry().width, 32)

		# TODO: Move to top of screen, make always-on-top
		# Tried doing this with python-xlib but encountered issues, see
		# https://github.com/python-xlib/python-xlib/issues/219
