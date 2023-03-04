# coding: utf-8
"""
Notepad plugin for Aspinwall
"""
from aspinwall_launcher.widgets import Widget
from gi.repository import Gtk
translatable = lambda message: message

class Notepad(Widget):
    metadata = {
        "name": translatable("Notepad"),
        "icon": 'accessories-text-editor-symbolic',
        "description": translatable("Take small notes"),
        "id": "org.dithernet.aspinwall.widgets.Notepad",
        "tags": translatable('notes,todo,to do,list'),
        "author": translatable("Aspinwall developers"),
        "url": "https://github.com/aspinwall-ui/aspinwall-launcher",
        "issue_tracker": "https://github.com/aspinwall-ui/aspinwall-launcher/issues",
        "version": "0.0.1"
    }

    has_config = True
    has_stylesheet = True
    no_padding = True

    def __init__(self, instance=0):
        super().__init__(instance)

        scroll = Gtk.ScrolledWindow(hexpand=True, min_content_height=200, max_content_height=200)

        self.textview = Gtk.TextView(
            hexpand=True,
            vexpand=True,
            pixels_above_lines=6,
            pixels_inside_wrap=2,
            accepts_tab=False
        )
        self.textview.set_wrap_mode(Gtk.WrapMode.WORD_CHAR)
        self.textview.add_css_class('notepad-text')
        self.textview.get_buffer().set_enable_undo(True)
        self.textview.get_buffer().set_text(self.config['buffer'])

        self.textview.get_buffer().connect('changed', self.save)

        scroll.set_child(self.textview)
        self.set_child(scroll)

    def save(self, *args):
        """Saves the contents of the notepad."""
        textbuffer = self.textview.get_buffer()
        self.config['buffer'] = textbuffer.get_text(
            textbuffer.get_start_iter(),
            textbuffer.get_end_iter(),
            False
        )

_widget_class = Notepad
