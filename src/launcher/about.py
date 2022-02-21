# coding: utf-8
"""
Contains code for the launcher settings window. Not to be confused with the
settings access backend, which is set up in config.py.
"""
from gi.repository import Gtk

@Gtk.Template(resource_path='/org/dithernet/aspinwall/launcher/ui/about.ui')
class AboutAspinwall(Gtk.AboutDialog):
	"""About dialog."""
	__gtype_name__ = 'AboutAspinwall'

	def _about_response(self, *args):
		self.destroy()
