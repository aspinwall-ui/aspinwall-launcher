# coding: utf-8
"""
Welcome plugin for Aspinwall
"""
from aspinwall.widgets import Widget
from gi.repository import Gtk, Adw

class Welcome(Widget):
	metadata = {
		"name": "Welcome",
		"icon": 'dialog-information-symbolic',
		"description": "Displays basic information about Aspinwall.",
		"id": "org.dithernet.aspinwall.widgets.Welcome",
		"tags": 'welcome,first startup'
	}

	def __init__(self, instance=0):
		super().__init__(instance)
		_ = self.l

		header = Gtk.Label(
			label=_('Welcome to Aspinwall'),
			use_markup=True, hexpand=True,
			margin_top=10, margin_bottom=10
		)
		header.add_css_class('large-title')
		self.content.append(header)

		info_clamp = Adw.Clamp(maximum_size=700)
		info = Gtk.Box(hexpand=True, orientation=Gtk.Orientation.VERTICAL)
		info_clamp.set_child(info)

		thankyou = Gtk.Label(
			label=_("Thank you for trying out Aspinwall! The UI is still in active development, and some things may not work correctly - you can report bugs to <a href='https://github.com/aspinwall-ui/aspinwall/issues'>our bug tracker</a>."), # noqa: E501
			wrap=True, use_markup=True
		)
		thankyou.add_css_class('body')

		widgetguide = Gtk.Box(hexpand=True)

		widgetguide = Gtk.Label(
			label=_("""
• To add a new widget, press the menu button in the top right corner, then select “Add Widgets”.
• To remove this widget, long-press it and click the trash icon on the toolbar that pops up.
"""), # noqa: E501
			wrap=True
		)

		widgetguide.add_css_class('body')
		widgetguide.add_css_class('welcome-text')

		info.append(thankyou)
		info.append(widgetguide)

		self.content.append(info_clamp)

_widget_class = Welcome
