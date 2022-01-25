# coding: utf-8
"""
Welcome plugin for Aspinwall
"""
from aspinwall.widgets import Widget
from gi.repository import Gtk

class Welcome(Widget):
	metadata = {
		"name": "Welcome",
		"icon": 'dialog-information-symbolic',
		"description": "Displays basic information about Aspinwall.",
		"id": "org.dithernet.aspinwall.welcome"
	}

	config = False

	def __init__(self, config={}):
		super().__init__()

		container = Gtk.Box(halign=Gtk.Align.FILL, hexpand=True)
		container.append(Gtk.Label(label='To add new widgets, press the '))
		container.append(Gtk.Image.new_from_icon_name('open-menu-symbolic'))
		container.append(Gtk.Label(label=' button in the top right corner.'))

		self.content = container

_widget_class = Welcome
