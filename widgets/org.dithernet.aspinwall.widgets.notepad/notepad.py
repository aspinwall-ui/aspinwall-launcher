# coding: utf-8
"""
Notepad plugin for Aspinwall
"""
from aspinwall.widgets import Widget
from gi.repository import Gtk

class Notepad(Widget):
	metadata = {
		"name": "Notepad",
		"icon": 'edit-paste-symbolic',
		"description": "Notepad",
		"id": "org.dithernet.aspinwall.widgets.Notepad",
		"tags": 'notes,todo,to do,list'
	}

	has_config = True

	def __init__(self, instance=0):
		super().__init__(instance)

		scroll = Gtk.ScrolledWindow(hexpand=True, min_content_height=200, max_content_height=200)

		self.textview = Gtk.TextView(hexpand=True, vexpand=True)
		self.textview.set_wrap_mode(Gtk.WrapMode.WORD_CHAR)
		self.textview.get_buffer().set_enable_undo(True)
		self.textview.get_buffer().set_text(self.config['buffer'])

		self.textview.get_buffer().connect('changed', self.save)

		scroll.set_child(self.textview)
		self.content.append(scroll)

	def save(self, *args):
		"""Saves the contents of the notepad."""
		textbuffer = self.textview.get_buffer()
		self.config['buffer'] = textbuffer.get_text(
			textbuffer.get_start_iter(),
			textbuffer.get_end_iter(),
			False
		)

_widget_class = Notepad
