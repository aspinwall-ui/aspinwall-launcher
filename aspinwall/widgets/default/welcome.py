# coding: utf-8
"""
Welcome plugin for Aspinwall
"""
from aspinwall.widgets import Widget
from gi.repository import Gtk

class Welcome(Widget):
	title = "Welcome to Aspinwall"
	icon = 'dialog-information'
	metadata = {
		"name": "Welcome",
		"description": "Editable welcome widget; displays a simple tutorial and any distro-specific text",
		"id": "org.dithernet.aspinwall.welcome"
	}

	def __init__(self, config={}):
		super().__init__()

		container = Gtk.Box(halign=Gtk.Align.FILL, hexpand=True)
		container.append(Gtk.Label(label='To add new widgets, press the '))
		container.append(Gtk.Image.new_from_icon_name('open-menu-symbolic'))
		container.append(Gtk.Label(label=' button in the top right corner.'))

		self.append(container)

_widget_class = Welcome
