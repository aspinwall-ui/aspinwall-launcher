# coding: utf-8
"""
Contains the code for the panel.
"""
from gi.repository import Gtk

from aspinwall.shell.surface import Surface

@Gtk.Template(resource_path='/org/dithernet/aspinwall/shell/ui/panel.ui')
class Panel(Surface):
	"""The status bar on the top of the screen."""
	__gtype_name__ = 'Panel'

	def __init__(self, app):
		"""Initializes the panel."""
		super().__init__(application=app, hexpand=True, height=32)
